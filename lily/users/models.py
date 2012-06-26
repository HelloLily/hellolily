from django.contrib import messages
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.signals import user_logged_out
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.utils.functions import get_tenant_mixin as TenantMixin
from lily.utils.models import EmailAddress

try:
    from lily.tenant.functions import add_tenant
except ImportError:
    from lily.utils.functions import dummy_function as add_tenant


class CustomUser(User, TenantMixin):
    """
    Custom user model, has relation with Contact.
    """
    objects = UserManager()
    contact = models.ForeignKey(Contact, related_name='user')
    account = models.ForeignKey(Account, related_name='user')
    
    def __unicode__(self):
        return unicode(self.contact)
    
    def __getattribute__(self, name):
        if name == 'primary_email':
            try:
                if self.contact:
                    email = self.contact.email_addresses.get(is_primary=True)
                    return email.email_address
            except EmailAddress.DoesNotExist:
                pass
            return None
        else:
            return object.__getattribute__(self, name)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['contact']
        permissions = (
            ("send_invitation", _("Can send invitations to invite new users")),
        )


## ------------------------------------------------------------------------------------------------
## Signal listeners
## ------------------------------------------------------------------------------------------------

@receiver(pre_save, sender=CustomUser)
def post_save_customuser_handler(sender, **kwargs):
    """
    If an e-mail attribute was set on an instance of CustomUser, add a primary e-mail address or 
    overwrite the existing one.
    """
    instance = kwargs['instance']
    if instance.__dict__.has_key('primary_email'):
        new_email_address = instance.__dict__['primary_email'];
        if len(new_email_address.strip()) > 0:
            try:
                # Overwrite existing primary e-mail address
                email = instance.contact.email_addresses.get(is_primary=True)
                email.email_address = new_email_address
                email.save()
            except EmailAddress.DoesNotExist:
                # Add new e-mail address as primary
                email = EmailAddress(email_address=new_email_address, is_primary=True)
                add_tenant(email, instance.tenant)
                email.save()
                instance.contact.email_addresses.add(email)

@receiver(user_logged_out)
def logged_out_callback(sender, **kwargs):
    request = kwargs['request']
    messages.info(request, _('You are now logged out.'))