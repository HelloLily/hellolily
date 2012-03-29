from django.db import models
from django.utils.translation import ugettext as _
from lily.utils.models import CommonModel


ACCOUNT_UPLOAD_TO = 'images/profile/account'


class TagModel(models.Model):
    """
    Tag model, simple char field to store a tag. Is used to describe the model it is linked to.
    """
    
    tag = models.CharField(max_length=50, verbose_name=_('tag'))

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
    tags = models.ManyToManyField(TagModel, verbose_name=_('list of tags'))
    logo = models.ImageField(upload_to=ACCOUNT_UPLOAD_TO, verbose_name=_('logo'), blank=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


