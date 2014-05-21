import operator

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext as _

from lily.settings import ACCOUNT_UPLOAD_TO
from lily.tags.models import TaggedObjectMixin
from lily.utils.functions import flatten
from lily.utils.models import Common, EmailAddress, CaseClientModelMixin
from python_imap.folder import ALLMAIL, SENT, IMPORTANT, INBOX
try:
    from lily.tenant.functions import add_tenant
except ImportError:
    from lily.utils.functions import dummy_function as add_tenant


class Account(Common, TaggedObjectMixin, CaseClientModelMixin):
    """
    Account model, this is a company's profile. May have relations with contacts.
    """
    STATUS_CHOICES = (
        # TODO: translate statuses (nl->en)
        # # ooit contact mee geweest | contacted
        # # actief offerte traject | being billed
        # # offerte gehad | billed
        # # actieve klant | active customer
        # # klant met betalingsachterstand | arrears
        # # failliet | bankrupt
        # # oud klant | previous customer.
        ('bankrupt', _('bankrupt')),
        ('prev_customer', _('previous customer')),
    )

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

    customer_id = models.CharField(max_length=32, verbose_name=_('customer id'), blank=True)
    name = models.CharField(max_length=255, verbose_name=_('company name'))
    flatname = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name=_('status'),
                              blank=True)
    company_size = models.CharField(max_length=15, choices=ACCOUNT_SIZE_CHOICES,
                                    verbose_name=_('company size'), blank=True)
    logo = models.ImageField(upload_to=ACCOUNT_UPLOAD_TO, verbose_name=_('logo'), blank=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    legalentity = models.CharField(max_length=20, verbose_name=_('legal entity'), blank=True)
    taxnumber = models.CharField(max_length=20, verbose_name=_('tax number'), blank=True)
    bankaccountnumber = models.CharField(max_length=20, verbose_name=_('bank account number'), blank=True)
    cocnumber = models.CharField(max_length=10, verbose_name=_('coc number'), blank=True)
    iban = models.CharField(max_length=40, verbose_name=_('iban'), blank=True)
    bic = models.CharField(max_length=20, verbose_name=_('bic'), blank=True)

    def primary_email(self):
        for email in self.email_addresses.all():
            if email.is_primary:
                return email
        return None

    def get_work_phone(self):
        for phone in self.phone_numbers.all():
            if phone.type == 'work':
                return phone
        return None

    def get_mobile_phone(self):
        for phone in self.phone_numbers.all():
            if phone.type == 'mobile':
                return phone
        return None

    def get_phone_number(self):
        """
        Return a phone number for an account in the order of:
        - a work phone
        - mobile phone
        - any other existing phone number (except of the type fax or data)
        """
        work_phone = self.get_work_phone()
        if work_phone:
            return work_phone

        mobile_phone = self.get_mobile_phone()
        if mobile_phone:
            return mobile_phone

        try:
            return self.phone_numbers.filter(type__in=['work', 'mobile', 'home', 'pager', 'other'])[0]
        except:
            return None

    def get_addresses(self, type=None):
        try:
            if type is None:
                return self.addresses.all()
            else:
                return self.addresses.filter(type=type)
        except:
            return None

    def get_billing_addresses(self):
        return self.get_addresses(type='billing')

    def get_shipping_addresses(self):
        return self.get_addresses(type='shipping')

    def get_visiting_addresses(self):
        return self.get_addresses(type='visiting')

    def get_other_addresses(self):
        return self.get_addresses(type='other')

    def get_deals(self, stage=None):
        try:
            if stage is None:
                return self.deal_set.all()
            else:
                return self.deal_set.filter(stage=stage)
        except:
            return None

    def get_deals_new(self):
        return self.get_deals(stage=0)

    def get_deals_lost(self):
        return self.get_deals(stage=1)

    def get_deals_pending(self):
        return self.get_deals(stage=2)

    def get_deals_won(self):
        return self.get_deals(stage=3)

    def get_contact_details(self):
        try:
            phone = self.phone_numbers.filter(status=1)[0]
            phone = phone.number
        except:
            phone = None

        try:
            email = self.primary_email
        except:
            email = None

        return {
            'phone': phone,
            'mail': email,
        }

    def get_twitter(self):
        try:
            return self.social_media.filter(name='twitter')[0]
        except:
            return ''

    def get_contacts(self):
        functions = self.functions.all()
        contacts = []
        for function in functions:
            contacts.append(function.contact)

        return contacts

    def get_email_count(self):
        from lily.messaging.email.models import EmailMessage
        try:
            filter_list = [Q(headers__value__contains=x) for x in self.email_addresses.all()]
            object_list = EmailMessage.objects.filter(
                Q(folder_identifier__in=[ALLMAIL, SENT, IMPORTANT, INBOX]) &
                Q(headers__name__in=['To', 'From', 'CC', 'Delivered-To', 'Sender']) &
                reduce(operator.or_, filter_list)
            )

            if object_list:
                return object_list.count()
        except:
            return 0

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Save account name in flatname
        self.flatname = flatten(self.name)

        return super(Account, self).save(*args, **kwargs)

    email_template_parameters = [name, description, ]
    email_template_lookup = 'request.user.account'

    class Meta:
        ordering = ['name']
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


class Website(models.Model):
    """
    Website model, simple url field to store a website reference.
    """
    website = models.URLField(max_length=255, verbose_name=_('website'))
    account = models.ForeignKey(Account, related_name='websites')
    is_primary = models.BooleanField(default=False, verbose_name=_('primary website'))

    def __unicode__(self):
        return self.website

    class Meta:
        verbose_name = _('website')
        verbose_name_plural = _('websites')


## ------------------------------------------------------------------------------------------------
## Signal listeners
## ------------------------------------------------------------------------------------------------

@receiver(pre_save, sender=Account)
def post_save_account_handler(sender, **kwargs):
    """
    If an e-mail attribute was set on an instance of Account, add a primary e-mail address or
    overwrite the existing one.
    """
    instance = kwargs['instance']
    if instance.__dict__.has_key('primary_email'):
        new_email_address = instance.__dict__['primary_email']
        if len(new_email_address.strip()) > 0:
            try:
                # Overwrite existing primary e-mail address
                email = instance.email_addresses.get(is_primary=True)
                email.email_address = new_email_address
                email.save()
            except EmailAddress.DoesNotExist:
                # Add new e-mail address as primary
                email = EmailAddress(email_address=new_email_address, is_primary=True)
                add_tenant(email, instance.tenant)
                email.save()
                instance.email_addresses.add(email)
