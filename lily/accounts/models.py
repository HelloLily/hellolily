from django.db import models
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext as _
from lily.utils.models import CommonModel, EmailAddressModel


ACCOUNT_UPLOAD_TO = 'images/profile/account'


class TagModel(models.Model):
    """
    Tag model, simple char field to store a tag. Is used to describe the model it is linked to.
    """
    
    tag = models.CharField(max_length=50, verbose_name=_('tag'))

    def __unicode__(self):
        return self.tag
    
    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')


class AccountModel(CommonModel):
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
    
    COMPANY_SIZE_CHOICES = (
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
    website = models.URLField(verbose_name=_('company\'s website'), blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name=_('status'),
                              blank=True)
    company_size = models.CharField(max_length=15, choices=COMPANY_SIZE_CHOICES,
                                    verbose_name=_('company size'), blank=True)  
    tags = models.ManyToManyField(TagModel, verbose_name=_('tags'), blank=True)
    logo = models.ImageField(upload_to=ACCOUNT_UPLOAD_TO, verbose_name=_('logo'), blank=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    
    def __unicode__(self):
        return self.name
    
    def get_address(self):
        try:
            address = self.addresses.all()[0]
            return {
                'address': '%s %s' % (address.street, address.street_number),
                'country': address.country,
            }
        except:
            return {
                'address': '-',
                'country': '-',
            }
    
    def get_contact_details(self):
        try:
            phone = self.phone_numbers.filter(status=1)[0]
            phone = phone.number
        except:
            phone = '-'   
        
        try:
            email = self.email_addresses.filter(is_primary=True, status=1)[0]
            email = email.email_address
        except:
            email = '-'
        
        return {
            'phone': phone,
            'mail': email,
        }
    
    def get_tags(self):
        try:
            tags = self.tags.all()[:3]
#            tags = (tags[0].tag, tags[1].tag, tags[1].tag,)
        except:
            tags = ('',)
        return tags

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


## ------------------------------------------------------------------------------------------------
## Signal listeners
## ------------------------------------------------------------------------------------------------

@receiver(pre_save, sender=AccountModel)
def post_save_usermodel_handler(sender, **kwargs):
    """
    If an e-mail attribute was set on an instance of UserModel, add a primary e-mail address or 
    overwrite the existing one.
    """
    instance = kwargs['instance']
    if instance.__dict__.has_key('email'):
        new_email_address = instance.__dict__['email'];
        try:
            # Overwrite existing primary e-mail address
            email = instance.email_addresses.get(is_primary=True)
            email.email_address = new_email_address
            email.save()
        except EmailAddressModel.DoesNotExist:
            # Add new e-mail address as primary
            email = EmailAddressModel.objects.create(email_address=new_email_address, is_primary=True)
            instance.email_addresses.add(email)
