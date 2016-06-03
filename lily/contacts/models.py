from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from django.conf import settings
from lily.tags.models import TaggedObjectMixin
from lily.utils.models.models import PhoneNumber, EmailAddress
from lily.utils.models.mixins import Common, DeletedMixin, CaseClientModelMixin
try:
    from lily.tenant.functions import add_tenant
except ImportError:
    from lily.utils.functions import dummy_function as add_tenant


def get_contact_picture_upload_path(instance, filename):
    return settings.CONTACT_PICTURE_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'contact_id': instance.pk,
        'filename': filename
    }


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

    first_name = models.CharField(max_length=255, verbose_name=_('first name'), default='', blank=True)
    preposition = models.CharField(max_length=100, verbose_name=_('preposition'), default='', blank=True)
    last_name = models.CharField(max_length=255, verbose_name=_('last name'), default='', blank=True)
    gender = models.IntegerField(choices=CONTACT_GENDER_CHOICES, default=UNKNOWN_GENDER,
                                 verbose_name=_('gender'))
    title = models.CharField(max_length=20, verbose_name=_('title'), blank=True)
    status = models.IntegerField(choices=CONTACT_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))
    picture = models.ImageField(upload_to=get_contact_picture_upload_path, verbose_name=_('picture'), blank=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    salutation = models.IntegerField(choices=SALUTATION_CHOICES, default=INFORMAL, verbose_name=_('salutation'))

    import_id = models.CharField(max_length=100, default='', blank=True, db_index=True)
    accounts = models.ManyToManyField(
        Account,
        through='Function',
        through_fields=('contact', 'account'),
        related_name='contacts',
    )

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model
        """
        return ContentType.objects.get(app_label='contacts', model='contact')

    @property
    def primary_email(self):
        """
        Will return the primary email address set to this contact if one exists.

        Returns:
            EmailAddress or empty string.
        """
        if not hasattr(self, '_primary_email'):
            self._primary_email = self.email_addresses.filter(status=EmailAddress.PRIMARY_STATUS).first()

            if not self._primary_email:
                self._primary_email = ''

        return self._primary_email

    @property
    def account_city(self):
        city = ''
        account = self.accounts.first()

        if account:
            city = account.main_address.city

        return city

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
    def full_name(self):
        """
        Return full name of this contact without unnecessary white space.
        """
        if self.preposition:
            return ' '.join([self.first_name, self.preposition, self.last_name]).strip()

        return ' '.join([self.first_name, self.last_name]).strip()

    def __unicode__(self):
        return self.full_name

    EMAIL_TEMPLATE_PARAMETERS = ['first_name', 'preposition', 'last_name', 'full_name', 'twitter', 'linkedin',
                                 'work_phone', 'mobile_phone', 'primary_email', 'account_city']

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
    If an email attribute was set on an instance of Contact, add a primary email address or
    overwrite the existing one.
    """
    instance = kwargs['instance']
    if 'primary_email' in instance.__dict__:
        new_email_address = instance.__dict__['primary_email']
        if len(new_email_address.strip()) > 0:
            # Overwrite existing primary email address
            email = instance.email_addresses.filter(status=EmailAddress.PRIMARY_STATUS).first()
            if email:
                email.email_address = new_email_address
                email.save()
            else:
                # Add new email address as primary
                email = EmailAddress(email_address=new_email_address, status=EmailAddress.PRIMARY_STATUS)
                add_tenant(email, instance.tenant)
                email.save()
                instance.email_addresses.add(email)
