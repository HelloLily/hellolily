from django.contrib import messages
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.signals import user_logged_out
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from lily.contacts.models import ContactModel
from lily.utils.models import EmailAddressModel


USER_UPLOAD_TO = 'images/profile/user'


class UserModel(User):
    """
    Custom user model, has relation with ContactModel.
    """
        
    objects = UserManager()
    avatar = models.ImageField(upload_to=USER_UPLOAD_TO, verbose_name=_('avatar'), blank=True)
    contact = models.ForeignKey(ContactModel)
    
    def __unicode__(self):
        return unicode(self.contact)
    
    def __getattribute__(self, name):
        if name == 'email':
            try:
                if self.contact:
                    email = self.contact.email_addresses.get(is_primary=True)
                    return email.email_address
            except EmailAddressModel.DoesNotExist:
                pass
            return None
        else:
            return object.__getattribute__(self, name)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


## ------------------------------------------------------------------------------------------------
## Signal listeners
## ------------------------------------------------------------------------------------------------

@receiver(pre_save, sender=UserModel)
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
            email = instance.contact.email_addresses.get(is_primary=True)
            email.email_address = new_email_address
            email.save()
        except EmailAddressModel.DoesNotExist:
            # Add new e-mail address as primary
            email = EmailAddressModel.objects.create(email_address=new_email_address, is_primary=True)
            instance.contact.email_addresses.add(email)

@receiver(user_logged_out)
def logged_out_callback(sender, **kwargs):
    request = kwargs['request']
    messages.info(request, _('You have succesfully logged out.'))