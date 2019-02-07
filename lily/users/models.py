import calendar
import hashlib
import hmac
from datetime import datetime, timedelta

import analytics
import avinit
import chargebee
import pytz
import requests
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, PermissionsMixin, Group
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField

from lily.socialmedia.models import SocialMedia
from lily.tenant.models import TenantMixin, Tenant, TenantManager
from lily.utils.models.models import Webhook


class LilyUserManager(TenantManager, UserManager):
    """
    The user model that is used everywhere.
    """
    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing it.
        """
        return email.lower()

    def _create_user(self, email, password, tenant_id, **extra_fields):
        """
        Creates and saves a User with the given email, password and extra fields.
        """
        now = timezone.now()
        email = self.normalize_email(email)
        password = make_password(password)

        # Create default onboarding info.
        user_info = UserInfo.objects.create()

        picture = extra_fields.pop('picture', None)

        user = self.create(
            tenant_id=tenant_id,
            email=email,
            password=password,
            last_login=now,
            date_joined=now,
            info=user_info,
            **extra_fields
        )

        if not picture:
            gravatar_hash = hashlib.md5(email.encode('utf-8', errors='replace')).hexdigest()
            response = requests.get('https://secure.gravatar.com/avatar/{}'.format(gravatar_hash), params={
                'default': '404',
                'size': '200'
            })

            if response.status_code == requests.codes.ok:
                extension = response.headers.get('Content-Type', '/').split('/')[-1]

                if extension:
                    picture = ContentFile(
                        content=response.content,
                        name='profile-picture.{}'.format(extension)
                    )

        if picture:
            user.picture.save(picture.name, picture)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Prepare the creation of a new user.
        """
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        tenant = extra_fields.pop('tenant', None)
        tenant_id = extra_fields.pop('tenant_id', None)

        if tenant and tenant_id:
            raise ValueError('Parameters are mutually exclusive: tenant and tenant_id')

        if tenant:
            tenant_id = tenant.pk

        with transaction.atomic():
            new_tenant_created = False
            if not tenant_id:
                new_tenant_created = True
                tenant = Tenant.create_tenant(domain=email)

                tenant_id = tenant.pk

            extra_fields['tenant_id'] = tenant_id

            user = self._create_user(email, password, **extra_fields)

            if new_tenant_created:
                # Add the user to the admin group.
                account_admin = Group.objects.get_or_create(name='account_admin')[0]
                user.groups.add(account_admin)

                # Start a trial for this user/tenant.
                if settings.BILLING_ENABLED:
                    trial_end = datetime.now() + timedelta(days=30)
                    # Chargebee wants the time in seconds.
                    trial_end_seconds = calendar.timegm(trial_end.timetuple())

                    result = chargebee.Subscription.create({
                        'plan_id': tenant.billing.plan.name,
                        'trial_end': trial_end_seconds,
                        'customer': {
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'email': user.email,
                            'company': tenant.name,
                        },
                    })

                    tenant.billing.customer_id = result.customer.id
                    tenant.billing.subscription_id = result.subscription.id
                    tenant.billing.trial_end = trial_end
                    tenant.billing.save()

                    # Track subscription changes in Segment.
                    # It's a new subscription, so old_plan_tier param is missing.
                    analytics.track(user.id, 'subscription-changed', {
                        'tenant_id': tenant.id,
                        'new_plan_tier': tenant.billing.plan.tier,
                    })
            elif settings.BILLING_ENABLED:
                # No new tenant, but user was created so we update the current subscription.
                user.tenant.billing.update_subscription(1)

        return user

    def create_superuser(self, email, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, **extra_fields)


class Team(TenantMixin):
    """
    A group with a Tenant.
    """
    name = models.CharField(_('name'), max_length=80)

    def __unicode__(self):
        return self.name

    def active_users(self):
        return self.user_set.filter(is_active=True)

    class Meta:
        unique_together = ('tenant', 'name')


def get_lilyuser_picture_upload_path(instance, filename):
    return settings.LILYUSER_PICTURE_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'user_id': instance.pk,
        'filename': filename
    }


class UserInvite(TenantMixin):
    first_name = models.CharField(_('first name'), max_length=255)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)


class UserInfo(models.Model):
    INCOMPLETE, COMPLETE, SKIPPED = range(3)
    STATUS_CHOICES = (
        (INCOMPLETE, _('Incomplete')),
        (COMPLETE, _('Complete')),
        (SKIPPED, _('Skipped')),
    )

    registration_finished = models.BooleanField(
        verbose_name=_('User has finished the registration process'),
        default=False
    )
    # TODO: migration that removes this field.
    email_account_status = models.IntegerField(choices=STATUS_CHOICES, default=INCOMPLETE)


class LilyUser(TenantMixin, PermissionsMixin, AbstractBaseUser):
    """
    A custom user class implementing a fully featured User model with
    admin-compliant permissions.

    Password and email are required. Other fields are optional.
    """
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=255
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=255
    )
    picture = models.ImageField(
        upload_to=get_lilyuser_picture_upload_path,
        verbose_name=_('picture'),
        blank=True
    )
    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255,
        unique=True
    )
    position = models.CharField(
        verbose_name=_('position'),
        max_length=255,
        blank=True
    )
    is_staff = models.BooleanField(
        verbose_name=_('is staff'),
        default=False
    )
    is_active = models.BooleanField(
        verbose_name=_('is active'),
        default=True
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now
    )
    teams = models.ManyToManyField(
        to=Team,
        verbose_name=_('Lily teams'),
        blank=True,
        related_name='user_set',
        related_query_name='user',
    )
    phone_number = models.CharField(
        verbose_name=_('phone number'),
        max_length=40,
        blank=True
    )
    internal_number = models.PositiveSmallIntegerField(
        verbose_name=_('internal number'),
        blank=True,
        null=True
    )
    social_media = models.ManyToManyField(
        to=SocialMedia,
        verbose_name=_('list of social media'),
        blank=True
    )
    language = models.CharField(
        verbose_name=_('language'),
        max_length=3,
        choices=settings.LANGUAGES,
        default='en'
    )
    timezone = TimeZoneField(
        choices=[(pytz.timezone(tz), tz) for tz in pytz.common_timezones],
        max_length=63,
        default='Europe/Amsterdam'
    )

    primary_email_account = models.ForeignKey(
        to='email.EmailAccount',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    webhooks = models.ManyToManyField(
        to=Webhook,
        blank=True
    )
    info = models.ForeignKey(
        to=UserInfo,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    objects = LilyUserManager()
    all_objects = UserManager()

    EMAIL_TEMPLATE_PARAMETERS = [
        'first_name', 'last_name', 'full_name', 'position', 'phone_number', 'current_email_address', 'user_team',
        'profile_picture',
    ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(LilyUser, self).save(*args, **kwargs)

    def delete(self, using=None, hard=False):
        """
        Soft delete instance by flagging is_active as False.

        Arguments:
            using (str): which db to use
            hard (boolean): If True, permanent removal from db
        """
        if hard:
            super(LilyUser, self).delete(using=using)
        else:
            self.is_active = False
            self.save()

    @property
    def full_name(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        Return full name of this user without unnecessary white space.
        """
        return u' '.join([self.first_name, self.last_name]).strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    @property
    def profile_picture(self):
        if self.picture:
            return self.picture.url
        else:
            return avinit.get_avatar_data_url(self.full_name)

    @property
    def twitter(self):
        try:
            twitter = self.social_media.filter(name='twitter').first()
        except SocialMedia.DoesNotExist:
            pass
        else:
            return twitter.username

    @property
    def linkedin(self):
        try:
            linkedin = self.social_media.filter(name='linkedin').first()
        except SocialMedia.DoesNotExist:
            pass
        else:
            return linkedin.profile_url

    @property
    def user_team(self):
        user_team = self.teams.first()

        if not user_team:
            return ''

        return user_team

    @property
    def display_email_warning(self):
        return self.email_accounts_owned.filter(is_authorized=False, is_deleted=False).exists()

    @property
    def user_hash(self):
        return hmac.new(
            settings.INTERCOM_HMAC_SECRET,
            str(self.pk),
            digestmod=hashlib.sha256
        ).hexdigest()

    @property
    def is_admin(self):
        return self.groups.filter(name='account_admin').exists() or self.is_superuser

    def __unicode__(self):
        return self.full_name

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['first_name', 'last_name']
        permissions = (
            ('send_invitation', _('Can send invitations to invite new users')),
        )
        unique_together = ('tenant', 'internal_number')
