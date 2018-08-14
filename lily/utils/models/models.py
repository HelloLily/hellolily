from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.tenant.models import TenantMixin
from lily.utils.countries import COUNTRIES

PHONE_TYPE_CHOICES = (
    ('work', _('Work')),
    ('mobile', _('Mobile')),
    ('home', _('Home')),
    ('fax', _('Fax')),
    ('other', _('Other')),
)


class PhoneNumber(TenantMixin):
    """
    Phone number model, keeps a raw input version and a clean version (only has digits).
    """
    # TODO: check possibilities for integration of
    # - http://pypi.python.org/pypi/phonenumbers and/or
    # - https://github.com/stefanfoulis/django-phonenumber-field

    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    PHONE_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )

    number = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=PHONE_TYPE_CHOICES, default='work', verbose_name=_('type'))
    other_type = models.CharField(max_length=15, blank=True, null=True)  # used in combination with type='other'.
    status = models.PositiveSmallIntegerField(
        choices=PHONE_STATUS_CHOICES, default=ACTIVE_STATUS, verbose_name=_('status')
    )

    def __unicode__(self):
        return self.number

    class Meta:
        app_label = 'utils'
        verbose_name = _('phone number')
        verbose_name_plural = _('phone numbers')


class Address(TenantMixin):
    """
    Address model, has most default fields for an address and fixed preset values for type. In
    the view layer options are limited for different models. For example: options for an address
    for an account excludes 'home' as options for an address for a contact exclude 'visiting'.
    """
    ADDRESS_TYPE_CHOICES = (
        ('visiting', _('Visiting address')),
        ('billing', _('Billing address')),
        ('shipping', _('Shipping address')),
        ('home', _('Home address')),
        ('other', _('Other')),
    )

    address = models.CharField(max_length=255, verbose_name=_('address'), blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('postal code'), blank=True)
    city = models.CharField(max_length=100, verbose_name=_('city'), blank=True)
    state_province = models.CharField(max_length=50, verbose_name=_('state/province'), blank=True)
    # TODO: maybe try setting a default based on account/user preferences for country
    country = models.CharField(max_length=2, choices=COUNTRIES, verbose_name=_('country'), blank=True)
    type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, verbose_name=_('type'))

    def __unicode__(self):
        return u'%s' % (self.address or '')

    def country_display(self):
        return self.get_country_display() if self.country else ''

    def full(self):
        return u'%s %s %s' % (
            self.address or '',
            self.city or '',
            self.get_country_display() if self.country else '',
        )

    class Meta:
        app_label = 'utils'
        verbose_name = _('address')
        verbose_name_plural = _('addresses')


class EmailAddress(TenantMixin):
    """
    Email address model, it's possible to set an email address as primary address as a model can
    own multiple email addresses.
    """
    INACTIVE_STATUS, OTHER_STATUS, PRIMARY_STATUS = range(3)
    EMAIL_STATUS_CHOICES = (
        (PRIMARY_STATUS, _('Primary')),
        (OTHER_STATUS, _('Other')),
        (INACTIVE_STATUS, _('Inactive')),
    )

    email_address = models.EmailField(max_length=255, verbose_name=_('email address'))
    status = models.PositiveSmallIntegerField(
        choices=EMAIL_STATUS_CHOICES, default=OTHER_STATUS, verbose_name=_('status')
    )

    @property
    def is_active(self):
        return self.status != self.INACTIVE_STATUS

    def __unicode__(self):
        return self.email_address

    def save(self, *args, **kwargs):
        self.email_address = self.email_address.lower()
        super(EmailAddress, self).save(*args, **kwargs)

    class Meta:
        app_label = 'utils'
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')
        ordering = ['-status']


class ExternalAppLink(TenantMixin):
    """
    A link to an external app.
    """
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'utils'


class Webhook(TenantMixin):
    """
    A link to a webhook.
    """
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'utils'
