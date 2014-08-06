from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.users.models import CustomUser
from lily.tenant.models import TenantMixin
from lily.utils.models.mixins import Deleted, ArchivedMixin


class Deal(TenantMixin, Deleted, ArchivedMixin):
    """
    Deal model
    """
    CURRENCY_CHOICES = (
        ('EUR', _('Euro')),
        ('GBP', _('British pound')),
        ('NOR', _('Norwegian krone')),
        ('DKK', _('Danish krone')),
        ('SEK', _('Swedish krone')),
        ('CHF', _('Swiss franc')),
        ('USD', _('United States dollar')),
    )

    NEW_STAGE, LOST_STAGE, PENDING_STAGE, WON_STAGE = range(4)
    STAGE_CHOICES = (
        (NEW_STAGE, _('New')),
        (LOST_STAGE, _('Lost')),
        (PENDING_STAGE, _('Pending')),
        (WON_STAGE, _('Won')),
    )

    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    account = models.ForeignKey(Account, verbose_name=_('account'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR',
                                verbose_name=_('currency'))
    amount = models.DecimalField(max_digits=19, decimal_places=2, verbose_name=_('amount'))
    expected_closing_date = models.DateField(verbose_name=_('expected closing date'))
    closed_date = models.DateTimeField(verbose_name=_('closed date'), blank=True, null=True)
    stage = models.IntegerField(choices=STAGE_CHOICES, default=NEW_STAGE, verbose_name=_('status'))
    assigned_to = models.ForeignKey(CustomUser, verbose_name=_('assigned to'))
    notes = generic.GenericRelation('notes.Note', content_type_field='content_type',
                                    object_id_field='object_id', verbose_name='list of notes')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('deal')
        verbose_name_plural = _('deals')
