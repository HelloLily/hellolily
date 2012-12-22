from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext as _
from polymorphic import PolymorphicModel

from lily.users.models import CustomUser
from lily.utils.functions import get_tenant_mixin as TenantMixin


class MessagesAccount(PolymorphicModel, TimeStampedModel, TenantMixin):
    """
    A social media account base class, all accounts are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.
    """
    user_group = models.ManyToManyField(CustomUser, related_name='messages_accounts')
    account_type = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s account' % self.account_type

    class Meta:
        verbose_name = _('messages account')
        verbose_name_plural = _('messages accounts')


class Message(PolymorphicModel, TimeStampedModel, TenantMixin):
    """
    A message base class, all messages are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.
    """
    sent_date = models.DateTimeField(null=True)  # time sent in UTC
    is_seen = models.BooleanField(default=False)
    account = models.ForeignKey(MessagesAccount, related_name='messages')

    class Meta:
        abstract = True
        verbose_name = _('message')
        verbose_name_plural = _('messages')
