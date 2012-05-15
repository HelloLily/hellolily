from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField
from django_extensions.db.models import TimeStampedModel

from lily.multitenant.models import MultiTenantMixin


class Deleted(TimeStampedModel):
    """
    Deleted model, flags when an instance is deleted.
    """
    deleted = ModificationDateTimeField(_('deleted')) 
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True


class PhoneNumber(MultiTenantMixin, models.Model):
    """
    Phone number model, keeps a raw input version and a clean version (only has digits).
    """
    # TODO: check possibilities for integration of 
    # - http://pypi.python.org/pypi/phonenumbers and/or
    # - https://github.com/stefanfoulis/django-phonenumber-field
    
    PHONE_TYPE_CHOICES = (
        ('work', _('Work')),
        ('mobile', _('Mobile')),
        ('home', _('Home')),
        ('fax_home', _('Fax (home)')),
        ('fax_work', _('Fax (work)')),
        ('data', _('Data')),
        ('pager', _('Pager')),
        ('other', _('Other')),
    )
    
    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    PHONE_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )
    
    raw_input = models.CharField(max_length=40, verbose_name=_('phone number'))
    number = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=PHONE_TYPE_CHOICES, default='work', 
                            verbose_name=_('type'))
    other_type = models.CharField(max_length=15, blank=True, null=True) # used in combination with type='other'
    status = models.IntegerField(max_length=10, choices=PHONE_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))
    
    def __unicode__(self):
        return self.number
    
    def save(self, *args, **kwargs):
        # Save raw input as number only
        self.number = filter(type(self.raw_input).isdigit, self.raw_input)
        
        return super(PhoneNumber, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('phone number')
        verbose_name_plural = _('phone numbers')


class SocialMedia(MultiTenantMixin, models.Model):
    """
    Social media model, default supporting a few well known social media but has support for 
    custom input (other_name).
    """
    SOCIAL_NAME_CHOICES = (
        ('facebook', _('Facebook')),
        ('twitter', _('Twitter')),
        ('linkedin', _('LinkedIn')),
        ('googleplus', _('Google+')),
        ('qzone', _('Qzone')),
        ('orkut', _('Orkut')),
        ('other', _('Other')),
    )
    
    name = models.CharField(max_length=30,choices=SOCIAL_NAME_CHOICES, verbose_name=_('name'))
    other_name = models.CharField(max_length=30, blank=True, null=True) # used in combination with name='other'
    username = models.CharField(max_length=100, blank=True, verbose_name=_('username'))
    profile_url = models.URLField(verbose_name=_('profile link'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('social media')
        verbose_name_plural = _('social media')


class Address(MultiTenantMixin, models.Model):
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
    
    street = models.CharField(max_length=255, verbose_name=_('street'), blank=True)
    street_number = models.SmallIntegerField(verbose_name=_('street number'), blank=True, null=True)
    complement = models.CharField(max_length=10, verbose_name=_('complement'), blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('postal code'), blank=True)
    city = models.CharField(max_length=100, verbose_name=_('city'), blank=True)
    state_province = models.CharField(max_length=50, verbose_name=_('state/province'), blank=True)
    # TODO: maybe try setting a default based on account/user preferences for country
    country = models.CharField(max_length=200, verbose_name=_('country'), blank=True)
    type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, verbose_name=_('type'))

    def __unicode__(self):
        return u'%s %s %s' % (self.postal_code or '', self.street or '', self.street_number or '')

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')


class EmailAddress(MultiTenantMixin, models.Model):
    """
    Email address model, it's possible to set an email address as primary address as a model can 
    own multiple email addresses.
    """
    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    EMAIL_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )
    
    email_address = models.EmailField(max_length=255, verbose_name=_('e-mail address'))
    is_primary = models.BooleanField(default=False, verbose_name=_('primary e-mail'))
    status = models.IntegerField(max_length=50, choices=EMAIL_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))
    
    def __unicode__(self):
        return self.email_address

    class Meta:
        verbose_name = _('e-mail address')
        verbose_name_plural = _('e-mail addresses')


class Common(MultiTenantMixin, Deleted):
    """
    Common model to make it possible to easily define relations to other models.
    """
    phone_numbers = models.ManyToManyField(PhoneNumber, 
                                           verbose_name=_('list of phone numbers'))
    social_media = models.ManyToManyField(SocialMedia, verbose_name=_('list of social media'))
    addresses = models.ManyToManyField(Address, verbose_name=_('list of addresses'))
    email_addresses = models.ManyToManyField(EmailAddress,
                                             verbose_name=_('list of e-mail addresses'))
    notes = generic.GenericRelation('notes.Note', content_type_field='content_type',
                                    object_id_field='object_id', verbose_name='list of notes')
    
    class Meta:
        abstract = True


class Tag(MultiTenantMixin, models.Model):
    """
    Tag model, simple char field to store a tag. Is used to describe the model it is linked to.
    """
    tag = models.CharField(max_length=50, verbose_name=_('tag'))

    def __unicode__(self):
        return self.tag
    
    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
