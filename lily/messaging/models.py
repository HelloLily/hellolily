from django.db import models
from django.utils.translation import ugettext as _

from lily.users.models import LilyUser
from lily.tenant.middleware import get_current_user
from lily.tenant.models import PolymorphicTenantMixin, PolymorphicTenantManager
from lily.utils.models import HistoryListItem
from lily.utils.models.mixins import DeletedMixin


PRIVATE, PUBLIC, SHARED = range(3)
ACCOUNT_SHARE_CHOICES = [
    (PRIVATE, _('Don\'t share')),
    (PUBLIC, _('Everybody')),
    (SHARED, _('Specific users')),
]


class MessagesAccount(PolymorphicTenantMixin, DeletedMixin):
    """
    A social media account base class, all accounts are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.
    """
    account_type = models.CharField(max_length=255)
    shared_with = models.SmallIntegerField(choices=ACCOUNT_SHARE_CHOICES, default=0)
    user_group = models.ManyToManyField(LilyUser, related_name='messages_accounts_shared', verbose_name=_('shared with'))
    owner = models.ForeignKey(LilyUser, related_name='messages_accounts_owned', verbose_name=_('owner'))

    objects = PolymorphicTenantManager()

    @property
    def is_public(self):
        return self.shared_with == PUBLIC

    @property
    def is_shared(self):
        return self.shared_with == SHARED

    @property
    def is_private(self):
        return self.shared_with == PRIVATE

    @property
    def is_owned_by_user(self, user=None):
        return self.owner == (user or get_current_user())

    @property
    def is_shared_with_user(self, user=None):
        user = user or get_current_user()

        if not self.is_shared:
            return False

        return user in self.user_group.all()

    def __unicode__(self):
        return u'%s account' % self.account_type

    class Meta:
        verbose_name = _('messaging account')
        verbose_name_plural = _('messaging accounts')


class Message(HistoryListItem):
    """
    A message base class, all messages are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.
    """
    sent_date = models.DateTimeField(null=True)  # time sent in UTC
    is_seen = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.sort_by_date = self.sent_date
        return super(Message, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
