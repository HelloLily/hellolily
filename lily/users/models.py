from django.contrib.auth.models import User, UserManager
from django.db import models
from django.utils.translation import ugettext as _
from lily.contacts.models import ContactModel


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

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')