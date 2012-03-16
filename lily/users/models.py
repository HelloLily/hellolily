from django.contrib.auth.models import User, UserManager
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib import messages

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

    # TODO: overload setattribute to save self.email in EmailAdressModel as primary if it's the first e-mail address

    def __getattribute__(self, name):
        if name == 'email':
            try:
                if self.contact:
                    email = self.contact.email_addresses.get(is_primary=True)
                    return email.email_address
            except EmailAddressModel.DoesNotExist:
                # TODO: look into fixing super().email attribute as non-required field
                pass
            return 'nothing@interesting.com'
        else:
            return object.__getattribute__(self, name)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


## ------------------------------------------------------------------------------------------------
## Signal listeners
## ------------------------------------------------------------------------------------------------

@receiver(user_logged_out)
def logged_out_callback(sender, **kwargs):
    request = kwargs['request']
    messages.info(request, _('You have succesfully logged out.'))