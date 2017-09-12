from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from email_wrapper_lib.models.models import EmailAccount

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser, Team


class EmailAccountConfig(TenantMixin, models.Model):
    PUBLIC, METADATA, PRIVATE = range(3)
    PRIVACY_CHOICES = (
        (PUBLIC, _('Complete message')),
        (METADATA, _('Date and recipients')),
        (PRIVATE, _('Not at all')),
    )

    email_account = models.OneToOneField(
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
