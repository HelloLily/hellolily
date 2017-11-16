import hashlib
import hmac
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin, Group
from django.contrib.auth.signals import user_logged_out
from django.core.mail import send_mail
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField

from lily.socialmedia.models import SocialMedia
from lily.tenant.models import TenantMixin, Tenant
from lily.utils.models.models import Webhook


class LilyUserManager(UserManager):

    def _create_user(self, email, password, is_staff, is_superuser, tenant_id=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email address must be set')
        email = self.normalize_email(email)

        # Find or create a tenant.
        if tenant_id:
            # Don't use get_or_create.
            # Creating a tenant with the provided id collides with tenants created for the users in our test cases.
            tenant = Tenant.objects.get(pk=tenant_id)
        else:
            tenant = Tenant.objects.create()

        # Create default onboarding info.
        user_info = UserInfo.objects.create()

        user = self.model(tenant=tenant, email=email, is_staff=is_staff, is_active=True, is_superuser=is_superuser,
                          last_login=now, date_joined=now, info=user_info, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)

        account_admin = Group.objects.get_or_create(name='account_admin')[0]
        user.groups.add(account_admin)

        return user

    def get_by_natural_key(self, email):
        """"
        Define how the user should be retrieved.
        Default is to do a case sensitive match.
        """
        return self.get(email__iexact=email)


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

    email_account_status = models.IntegerField(choices=STATUS_CHOICES, default=INCOMPLETE)


class LilyUser(TenantMixin, PermissionsMixin, AbstractBaseUser):
    """
    A custom user class implementing a fully featured User model with
    admin-compliant permissions.

    Password and email are required. Other fields are optional.
    """
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    picture = models.ImageField(upload_to=get_lilyuser_picture_upload_path, verbose_name=_('picture'), blank=True)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    position = models.CharField(_('position'), max_length=255, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    teams = models.ManyToManyField(
        Team,
        verbose_name=_('Lily teams'),
        blank=True,
        related_name='user_set',
        related_query_name='user',
    )

    phone_number = models.CharField(_('phone number'), max_length=40, blank=True)
    internal_number = models.PositiveSmallIntegerField(_('internal number'), blank=True, null=True)
    social_media = models.ManyToManyField(SocialMedia, blank=True, verbose_name=_('list of social media'))

    language = models.CharField(_('language'), max_length=3, choices=settings.LANGUAGES, default='en')
    timezone = TimeZoneField(default='Europe/Amsterdam')

    primary_email_account = models.ForeignKey('email.EmailAccount', blank=True, null=True, on_delete=models.SET_NULL)
    webhooks = models.ManyToManyField(Webhook, blank=True)

    info = models.ForeignKey(UserInfo, blank=True, null=True, on_delete=models.SET_NULL)

    objects = LilyUserManager()

    EMAIL_TEMPLATE_PARAMETERS = ['first_name', 'last_name', 'full_name', 'position', 'twitter',
                                 'linkedin', 'phone_number', 'current_email_address', 'user_team', 'profile_picture']

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
            gravatar_hash = self.email.lower().encode('utf-8', errors='replace')
            gravatar_hash = hashlib.md5(gravatar_hash).hexdigest()

            # Try to get the Gravatar or show a default image if not available.
            gravatar_url = 'https://secure.gravatar.com/avatar/' + gravatar_hash + '?'
            gravatar_url += urllib.quote(urllib.urlencode({'d': 'mm', 's': str(200)}))

            return gravatar_url

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


@receiver(user_logged_out)
def logged_out_callback(sender, **kwargs):
    """
    Set a confirmation message in the request that the user is logged out successfully.
    """
    request = kwargs['request']
    messages.info(request, _('You are now logged out.'))
