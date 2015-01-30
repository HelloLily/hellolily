from django.db import models
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from django.conf import settings
from lily.tags.models import TaggedObjectMixin
from lily.utils.models import PhoneNumber, EmailAddress
from lily.utils.models.mixins import Common, DeletedMixin, CaseClientModelMixin
try:
    from lily.tenant.functions import add_tenant
except ImportError:
    from lily.utils.functions import dummy_function as add_tenant


class Contact(Common, TaggedObjectMixin, CaseClientModelMixin):
    """
    Contact model, this is a person's profile. Has an optional relation to an account through
    Function. Can be related to LilyUser.
    """
    MALE_GENDER, FEMALE_GENDER, UNKNOWN_GENDER = range(3)
    CONTACT_GENDER_CHOICES = (
        (MALE_GENDER, _('Male')),
        (FEMALE_GENDER, _('Female')),
        (UNKNOWN_GENDER, _('Unknown/Other')),
    )

    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    CONTACT_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )

    FORMAL, INFORMAL = range(2)
    SALUTATION_CHOICES = (
        (FORMAL, _('Formal')),
        (INFORMAL, _('Informal')),
    )

    first_name = models.CharField(max_length=255, verbose_name=_('first name'), blank=True)
    preposition = models.CharField(max_length=100, verbose_name=_('preposition'), blank=True)
    last_name = models.CharField(max_length=255, verbose_name=_('last name'), blank=True)
    gender = models.IntegerField(choices=CONTACT_GENDER_CHOICES, default=UNKNOWN_GENDER,
                                 verbose_name=_('gender'))
    title = models.CharField(max_length=20, verbose_name=_('title'), blank=True)
    status = models.IntegerField(choices=CONTACT_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))
    picture = models.ImageField(upload_to=settings.CONTACT_UPLOAD_TO, verbose_name=_('picture'), blank=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    salutation = models.IntegerField(choices=SALUTATION_CHOICES, default=INFORMAL, verbose_name=_('salutation'))

    def primary_email(self):
        if not hasattr(self, '_primary_email'):
            self._primary_email = None
            for email in self.email_addresses.all():
                if email.is_primary:
                    self._primary_email = email
        return self._primary_email

    def get_any_email_address(self):
        """
        Will return any email address set to this contact if one exists.

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

    def get_address(self, type=None):
        try:
            if not type:
                return self.addresses.all()[0]
            else:
                return self.addresses.filter(type=type)[0]
        except:
            return None

    def get_addresses(self, type=None):
        try:
            if not type:
                return self.addresses.all()
            else:
                return self.addresses.filter(type=type)
        except:
            return None

    def get_billing_addresses(self):
        return self.get_addresses(type='billing')

    def get_shipping_addresses(self):
        return self.get_addresses(type='shipping')

    def get_home_addresses(self):
        return self.get_addresses(type='home')

    def get_other_addresses(self):
        return self.get_addresses(type='other')

    def full_name(self):
        """
        Return full name of this contact without unnecessary white space.
        """
        if self.preposition:
            return ' '.join([self.first_name, self.preposition, self.last_name]).strip()

        return ' '.join([self.first_name, self.last_name]).strip()

    def get_primary_function(self):
        if not hasattr(self, '_primary_function'):
            try:
                self._primary_function = self.functions.all().order_by('-created')[0]
            except IndexError:
                self._primary_function = self.functions.none()
        return self._primary_function

    def __unicode__(self):
        return self.full_name()

    EMAIL_TEMPLATE_PARAMETERS = ['first_name', 'preposition', 'last_name', 'full_name', 'twitter', 'linkedin',
                                 'work_phone', 'mobile_phone']
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')


class Function(DeletedMixin):
    """
    Function, third model with extra fields for the relation between Account and Contact.
    """
    account = models.ForeignKey(Account, related_name='functions')
    contact = models.ForeignKey(Contact, related_name='functions')
    title = models.CharField(max_length=50, verbose_name=_('title'), blank=True)
    department = models.CharField(max_length=50, verbose_name=_('department'), blank=True)
    # Limited relation: only possible with contacts related to the same account
    manager = models.ForeignKey(Contact, related_name='manager', verbose_name=_('manager'),
                                blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    phone_numbers = models.ManyToManyField(PhoneNumber,
                                           verbose_name=_('list of phone numbers'))
    email_addresses = models.ManyToManyField(EmailAddress,
                                             verbose_name=_('list of email addresses'))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('function')
        verbose_name_plural = _('functions')
        unique_together = ('account', 'contact')

# ------------------------------------------------------------------------------------------------
# Signal listeners
# ------------------------------------------------------------------------------------------------


@receiver(pre_save, sender=Contact)
def post_save_contact_handler(sender, **kwargs):
    """
    If an e-mail attribute was set on an instance of Contact, add a primary e-mail address or
    overwrite the existing one.
    """
    instance = kwargs['instance']
    if 'primary_email' in instance.__dict__:
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
