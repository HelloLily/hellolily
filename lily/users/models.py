from django.contrib import messages
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin, Group
from django.contrib.auth.signals import user_logged_out
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext as _
from timezone_field import TimeZoneField

from lily.settings import LANGUAGES
from lily.tenant.models import TenantMixin, Tenant

try:
    from lily.tenant.functions import add_tenant
except ImportError:
    from lily.utils.functions import dummy_function as add_tenant


class LilyUserManager(UserManager):

    def _create_user(self, email, password, is_staff, is_superuser, tenant_pk=1, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email address must be set')
        email = self.normalize_email(email)

        # Find a tenant
        tenant = Tenant.objects.get_or_create(pk=tenant_pk)[0]

        user = self.model(tenant=tenant, email=email, is_staff=is_staff, is_active=True, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
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


class LilyUser(TenantMixin, PermissionsMixin, AbstractBaseUser):
    """
    A custom user class implementing a fully featured User model with
    admin-compliant permissions.

    Password and email are required. Other fields are optional.
    """
    first_name = models.CharField(_('first name'), max_length=45)
    preposition = models.CharField(_('preposition'), max_length=100, blank=True)
    last_name = models.CharField(_('last name'), max_length=45)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    phone_number = models.CharField(_('phone number'), max_length=40, blank=True)

    language = models.CharField(_('lanaguage'), max_length=3, choices=LANGUAGES, default='en')
    timezone = TimeZoneField(default='Europe/Amsterdam')

    objects = LilyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    def get_absolute_url(self):
        """
        Get the url to the user page
        """
        return reverse('dashboard')

    def get_full_name(self):
        """
        Return full name of this user without unnecessary white space.
        """
        if self.preposition:
            return u' '.join([self.first_name, self.preposition, self.last_name]).strip()

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

    def __unicode__(self):
        return self.get_full_name() or unicode(self.get_username())

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['first_name', 'last_name']
        permissions = (
            ("send_invitation", _("Can send invitations to invite new users")),
        )


@receiver(user_logged_out)
def logged_out_callback(sender, **kwargs):
    """
    Set a confirmation message in the request that the user is logged out successfully.
    """
    request = kwargs['request']
    messages.info(request, _('You are now logged out.'))
