import urlparse

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from lily.search.models import ElasticTenantManager
from lily.tags.models import TaggedObjectMixin
from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser
from lily.utils.functions import flatten, clean_website
from lily.utils.models.models import EmailAddress
from lily.utils.models.mixins import Common


def get_account_logo_upload_path(instance, filename):
    return settings.ACCOUNT_LOGO_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'account_id': instance.pk,
        'filename': filename
    }


class AccountStatus(TenantMixin):
    name = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = _('account statuses')
        ordering = ['position']


class Account(Common, TaggedObjectMixin):
    """
    Account model, this is a company's profile. May have relations with contacts.
    """
    ACCOUNT_SIZE_CHOICES = (
        ('1', u'1'),
        ('2', u'2-10'),
        ('11', u'11-50'),
        ('51', u'51-200'),
        ('201', u'201-1000'),
        ('1001', u'1001-5000'),
        ('5001', u'5001-10000'),
        ('10001', u'10001+'),
    )

    customer_id = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=255)
    flatname = models.CharField(max_length=255, blank=True)
    status = models.ForeignKey(AccountStatus, related_name='accounts')
    company_size = models.CharField(
        max_length=15,
        choices=ACCOUNT_SIZE_CHOICES,
        verbose_name=_('company size'),
        blank=True
    )
    logo = models.ImageField(upload_to=get_account_logo_upload_path, blank=True)
    description = models.TextField(blank=True)
    legalentity = models.CharField(max_length=20, blank=True)
    taxnumber = models.CharField(max_length=20, blank=True)
    bankaccountnumber = models.CharField(max_length=20, blank=True)
    cocnumber = models.CharField(max_length=20, blank=True)
    iban = models.CharField(max_length=40, blank=True)
    bic = models.CharField(max_length=20, blank=True)
    assigned_to = models.ForeignKey(LilyUser, null=True, blank=True, on_delete=models.SET_NULL)

    import_id = models.CharField(max_length=100, default='', blank=True, db_index=True)
    elastic_objects = ElasticTenantManager()

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model
        """
        return ContentType.objects.get(app_label="accounts", model="account")

    def primary_email(self):
        return self.email_addresses.filter(status=EmailAddress.PRIMARY_STATUS).first()

    @property
    def any_email_address(self):
        """
        Will return any email address set to this account if one exists.

        Check if there is a primary email address, if none are found,
        grab the first of the email address set.

        Returns:
            EmailAddress or None.
        """
        if not hasattr(self, '_any_email_address'):
            self._any_email_address = self.primary_email()
            if self._any_email_address is None:
                try:
                    self._any_email_address = self.email_addresses.all()[0]
                except IndexError:
                    pass
        return self._any_email_address

    @property
    def work_phone(self):
        for phone in self.phone_numbers.all():
            if phone.type == 'work':
                return phone
        return None

    @property
    def mobile_phone(self):
        for phone in self.phone_numbers.all():
            if phone.type == 'mobile':
                return phone
        return None

    @property
    def phone_number(self):
        """
        Return a phone number for an account in the order of:
        - a work phone
        - mobile phone
        - any other existing phone number (except of the type fax or data)
        """
        work_phone = self.work_phone
        if work_phone:
            return work_phone

        mobile_phone = self.mobile_phone
        if mobile_phone:
            return mobile_phone

        try:
            return self.phone_numbers.filter(type__in=['work', 'mobile', 'home', 'pager', 'other'])[0]
        except:
            return None

    @property
    def city(self):
        city = ''

        address = self.addresses.first()
        if address:
            city = address.city

        return city

    @property
    def address(self):
        address_full = ''

        address = self.addresses.first()
        if address:
            address_full = address.full

        return address_full

    def get_contacts(self):
        if not hasattr(self, '_contacts'):
            functions = self.functions.all()
            self._contacts = []
            for function in functions:
                if not (function.is_deleted or function.contact.is_deleted):
                    self._contacts.append(function.contact)

        return self._contacts

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Save account name in flatname
        self.flatname = flatten(self.name)

        return super(Account, self).save(*args, **kwargs)

    EMAIL_TEMPLATE_PARAMETERS = ['name', 'work_phone', 'any_email_address', 'city', 'address']

    class Meta:
        ordering = ['name']
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


class Website(TenantMixin, models.Model):
    """
    Website model, simple url field to store a website reference.
    """
    website = models.URLField(max_length=255, verbose_name=_('website'))
    account = models.ForeignKey(Account, related_name='websites')
    is_primary = models.BooleanField(default=False, verbose_name=_('primary website'))

    def __unicode__(self):
        return self.website

    @cached_property
    def full_domain(self):
        """Return the full domain name."""
        if not self.website:
            return None
        if not (self.website.startswith('http://') or self.website.startswith('https://')):
            return urlparse.urlparse('http://' + self.website.strip()).hostname
        else:
            return urlparse.urlparse(self.website.strip()).hostname

    @cached_property
    def second_level(self):
        """Return the second level domain."""
        second = self.full_domain
        if not second:
            return None
        if second.endswith('.co.uk') or second.endswith('.co.za'):
            second = '.'.join(second.split('.')[-3:-2])
        else:
            second = '.'.join(second.split('.')[-2:-1])
        return second

    def save(self, *args, **kwargs):
        self.website = clean_website(self.website)

        return super(Website, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('website')
        verbose_name_plural = _('websites')
