from django.db import models
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.settings import CONTACT_UPLOAD_TO
from lily.utils.models import Common, Deleted, PhoneNumber, EmailAddress


class Contact(Common):
    """
    Contact model, this is a person's profile. Has an optional relation to an account through
    Function. Can be related to CustomUser.
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
    
    def get_phonenumber(self):
        try:
            return self.phone_numbers.all()[0].raw_input
        except:
            return ''
    
    def get_work_phone(self):
        try:
            return self.phone_numbers.filter(type='work')[0].raw_input
        except:
            return ''
    
    def get_mobile_phone(self):
        try:
            return self.phone_numbers.filter(type='mobile')[0].raw_input
        except:
            return  ''
    
    def get_email(self):
        try:
            return self.email_addresses.all()[0].email_address
        except:
            return ''
    
    def get_social(self):
        try:
            return self.social_media.all()
        except:
            return {}
    
    def get_twitter(self):
        try:
            return self.social_media.filter(name='twitter')[0]
        except:
            return ''
    
    def get_primary_function(self):
        try:
            return self.functions.all().order_by('-created')[0]
        except:
            return ''
    
    def __unicode__(self):
        return self.full_name()
    
    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

   
class Function(Deleted):
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

## ------------------------------------------------------------------------------------------------
## Signal listeners
## ------------------------------------------------------------------------------------------------

@receiver(pre_save, sender=Contact)
def post_save_contact_handler(sender, **kwargs):
    """
    If an e-mail attribute was set on an instance of Contact, add a primary e-mail address or 
    overwrite the existing one.
    """
    instance = kwargs['instance']
    if instance.__dict__.has_key('primary_email'):
        new_email_address = instance.__dict__['primary_email'];
        if len(new_email_address.strip()) > 0:
            try:
                # Overwrite existing primary e-mail address
                email = instance.email_addresses.get(is_primary=True)
                email.email_address = new_email_address
                email.save()
            except EmailAddress.DoesNotExist:
                # Add new e-mail address as primary
                email = EmailAddress.objects.create(email_address=new_email_address, is_primary=True)
                instance.email_addresses.add(email)
