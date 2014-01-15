from datetime import datetime

from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tenant.models import TenantMixin
from lily.users.models import CustomUser
from lily.utils.models import Deleted


class Case(TenantMixin, Deleted):
    
    LOW_PRIO, MID_PRIO, HIGH_PRIO, CRIT_PRIO = range(4)
    PRIORITY_CHOICES = (
        (LOW_PRIO, _('Low')),
        (MID_PRIO, _('Medium')),
        (HIGH_PRIO, _('High')),
        (CRIT_PRIO, _('Critical')),
    )
    
    OPEN_STATUS, ASSIGNED_STATUS, PENDING_STATUS, CLOSED_STATUS = range(4)
    STATUS_CHOICES = (
        (OPEN_STATUS, _('Open')),
        (ASSIGNED_STATUS, _('In progress')),
        (PENDING_STATUS, _('Pending input')),
        (CLOSED_STATUS, _('Closed')),
    )
    
    priority = models.SmallIntegerField(choices=PRIORITY_CHOICES, verbose_name=_('priority'))
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=OPEN_STATUS, verbose_name=_('status'))
    
    assigned_to = models.ForeignKey(CustomUser, verbose_name=_('assigned to'))
    
    account = models.ForeignKey(Account, verbose_name=_('account'), blank=True, null=True)
    contact = models.ForeignKey(Contact, verbose_name=_('contact'), blank=True, null=True)
    
    notes = generic.GenericRelation('notes.Note', content_type_field='content_type',
                                    object_id_field='object_id', verbose_name='list of notes')

    expires = models.DateField(verbose_name=_('expires'), default=datetime.today)
    
    def __unicode__(self):
        return self.subject
    
    class Meta:
        verbose_name = _('case')
        verbose_name_plural = _('cases') 