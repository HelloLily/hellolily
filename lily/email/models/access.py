from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from email_wrapper_lib.models import EmailAccount

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser, Team


class EmailAccountConfig(TenantMixin, models.Model):
    PUBLIC, METADATA, PRIVATE = range(3)
    PRIVACY_CHOICES = (
        (PUBLIC, _('Complete message')),
        (METADATA, _('Date and recipients')),
        (PRIVATE, _('Not at all')),
    )

    email_account = models.ForeignKey(
        to=EmailAccount,
        on_delete=models.CASCADE,
        verbose_name=_('Email account'),
        related_name='config'
    )
    from_name = models.CharField(
        max_length=254,
        default='',
        verbose_name=_('From name'),
    )
    label = models.CharField(
        max_length=254,
        default='',
        verbose_name=_('Inbox label'),
    )

    # How do emails from this account appear in the activity stream.
    privacy = models.PositiveSmallIntegerField(
        choices=PRIVACY_CHOICES,
        default=PUBLIC,
        verbose_name=_('Privacy'),
    )

    # Sharing with other users and teams.
    owners = models.ManyToManyField(
        to=LilyUser,
        related_name='imelo_owned_email_accounts',
        verbose_name=_('Owned email accounts'),
    )
    shared_with_users = models.ManyToManyField(
        to=LilyUser,
        related_name='imelo_shared_email_accounts',
        verbose_name=_('Shared with users'),
    )
    shared_with_teams = models.ManyToManyField(
        to=Team,
        related_name='imelo_shared_email_accounts',
        verbose_name=_('Shared with teams'),
    )
    shared_with_everyone = models.BooleanField(
        default=False,
        verbose_name=_('Shared with everyone')
    )


class EmailAccountAccessCache(models.Model):
    """
    Model used to cache the access list of email accounts per user, so no expensive query is necessary to determine
    which accounts can be accessed. For performance this model uses plain stupid lists.
    """
    user = models.ForeignKey(
        to=LilyUser,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='email_account_access'
    )

    owned_accounts = JSONField(
        verbose_name=_('Accounts owned by user')
    )
    shared_accounts = JSONField(
        verbose_name=_('Accounts shared with user')
    )
    public_accounts = JSONField(
        verbose_name=_('Accounts made public to user')
    )

    def refresh(self):
        """
        Recalculate all the lists for the user and save them.
        """
        raise NotImplementedError
