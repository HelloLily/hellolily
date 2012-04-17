from django.db import models
from django.utils.translation import ugettext as _
from lily.accounts.models import AccountModel
from lily.settings import CONTACT_UPLOAD_TO
from lily.utils.models import CommonModel, DeletedModel, PhoneNumberModel, EmailAddressModel


class ContactModel(CommonModel):
    """
    Contact model, this is a person's profile. Has an optional relation to an account through
    FunctionModel. Can be related from UserModel.
    """
    MALE_GENDER, FEMALE_GENDER, UNKNOWN_GENDER = range(3)
    CONTACT_GENDER_CHOICES = (
        (MALE_GENDER, _('Male')),
        (FEMALE_GENDER, _('Female')),
        (UNKNOWN_GENDER, _('Unknown')),
    )
    
    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    CONTACT_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )
    
    first_name = models.CharField(max_length=255, verbose_name=_('first name'), blank=True)
    preposition = models.CharField(max_length=100, verbose_name=_('preposition'), blank=True)
    last_name = models.CharField(max_length=255, verbose_name=_('last name'), blank=True)
    gender = models.IntegerField(choices=CONTACT_GENDER_CHOICES, default=UNKNOWN_GENDER,
                                 verbose_name=_('gender'))
    title = models.CharField(max_length=20, verbose_name=_('title'), blank=True)
    status = models.IntegerField(choices=CONTACT_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))
    picture = models.ImageField(upload_to=CONTACT_UPLOAD_TO, verbose_name=_('picture'), blank=True)
    description = models.TextField(verbose_name=_('description'), blank=True)

    def full_name(self):
        """
        Return full name of this contact without unnecessary white space.
        """
        if self.preposition:
            return ' '.join([self.first_name, self.preposition, self.last_name])
        
        return ' '.join([self.first_name, self.last_name])

    def __unicode__(self):
        return self.full_name()
    
    def get_phonenumber(self):
        try:
            return self.phone_numbers.all()[0].raw_input
        except:
            return '-'
        
    def get_email(self):
        try:
            return self.email_addresses.all()[0].email_address
        except:
            return '-'
    
    def get_social(self):
        try:
            return self.social_media.all()
        except:
            return {}
    
    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

   
class FunctionModel(DeletedModel):
    """
    Function, third model with extra fields for the relation between Account and Contact.
    """
    account = models.ForeignKey(AccountModel, related_name='functions')
    contact = models.ForeignKey(ContactModel, related_name='functions')
    title = models.CharField(max_length=50, verbose_name=_('title'), blank=True)
    department = models.CharField(max_length=50, verbose_name=_('department'), blank=True)
    # Limited relation: only possible with contacts related to the same account 
    manager = models.ForeignKey(ContactModel, related_name='manager', verbose_name=_('manager'),
                                blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    phone_numbers = models.ManyToManyField(PhoneNumberModel,
                                           verbose_name=_('list of phone numbers'))
    email_addresses = models.ManyToManyField(EmailAddressModel,
                                             verbose_name=_('list of email addresses'))
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('function')
        verbose_name_plural = _('functions')
