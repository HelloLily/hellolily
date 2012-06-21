# Django imports
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext as _

# Lily imports
from lily.users.models import CustomUser

# 3rd party imports
from polymorphic import PolymorphicModel


class SocialMediaAccount(PolymorphicModel, TimeStampedModel):
    """
    A social media account base class, all accounts are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.

    """
    user_group = models.ManyToManyField(CustomUser, related_name='social_media_accounts')
    account_type = models.CharField(max_length=255)


    def __unicode__(self):
        return u'social media account'


    class Meta:
        verbose_name = _('social media account')
        verbose_name_plural = _('social media accounts')


class Message(PolymorphicModel, TimeStampedModel):
    """
    A message base class, all messages are subclasses of this base class.
    Automatically downcasts when queried so unicode is almost never used.

    """
    datetime = models.DateTimeField()
    is_seen = models.BooleanField(default=False)
    account = models.ForeignKey(SocialMediaAccount, related_name='messages')


    def __unicode__(self):
        return u'message'


    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')