from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext as _
from polymorphic import PolymorphicModel

from lily.users.models import CustomUser
from lily.utils.functions import get_tenant_mixin as TenantMixin
from lily.utils.models import HistoryListItem


ACCOUNT_SHARE_CHOICES = [
    (0, _('Don\'t share')),
    (1, _('Everybody')),
    (2, _('Specific users')),
]


class MessagesAccount(PolymorphicModel, TimeStampedModel, TenantMixin):
    """
    A social media account base class, all accounts are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.
    """
    account_type = models.CharField(max_length=255)
    shared_with = models.SmallIntegerField(choices=ACCOUNT_SHARE_CHOICES, default=0, help_text='')
    user_group = models.ManyToManyField(CustomUser, related_name='messages_accounts', verbose_name=_('users'))

    def __unicode__(self):
        return u'%s account' % self.account_type

    class Meta:
        verbose_name = _('messaging account')
        verbose_name_plural = _('messaging accounts')


class Message(HistoryListItem, TenantMixin):
    """
    A message base class, all messages are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.
    """
    sent_date = models.DateTimeField(null=True)  # time sent in UTC
    is_seen = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
