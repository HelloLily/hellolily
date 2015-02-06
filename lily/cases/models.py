from datetime import datetime

from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.parcels.models import Parcel
from lily.tags.models import TaggedObjectMixin
from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser
from lily.utils.models.mixins import DeletedMixin, ArchivedMixin


class CaseType(TenantMixin, ArchivedMixin):
    type = models.CharField(max_length=255, db_index=True)
    use_as_filter = models.BooleanField(default=True)  # whether it shows in the filter list or not

    def __unicode__(self):
        return self.type


class CaseStatus(TenantMixin):
    position = models.IntegerField()
    status = models.CharField(max_length=255)

    def __unicode__(self):
        return self.status

    class Meta:
        verbose_name_plural = _('case statuses')
        unique_together = ('tenant', 'position')
        ordering = ['position']


class Case(TenantMixin, TaggedObjectMixin, DeletedMixin, ArchivedMixin):
    LOW_PRIO, MID_PRIO, HIGH_PRIO, CRIT_PRIO = range(4)
    PRIORITY_CHOICES = (
        (LOW_PRIO, _('Low')),
        (MID_PRIO, _('Medium')),
        (HIGH_PRIO, _('High')),
        (CRIT_PRIO, _('Critical')),
    )

    priority = models.SmallIntegerField(choices=PRIORITY_CHOICES, verbose_name=_('priority'))
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    status = models.ForeignKey(CaseStatus, verbose_name=_('status'), related_name='cases')

    type = models.ForeignKey(CaseType, verbose_name=_('type'), null=True, blank=True, related_name='cases')

    assigned_to = models.ForeignKey(LilyUser, verbose_name=_('assigned to'), related_name='assigned_to', null=True, blank=True)
    created_by = models.ForeignKey(LilyUser, verbose_name=_('created by'), related_name='created_by', null=True, blank=True)

    account = models.ForeignKey(Account, verbose_name=_('account'), null=True, blank=True)
    contact = models.ForeignKey(Contact, verbose_name=_('contact'), null=True, blank=True)

    notes = generic.GenericRelation('notes.Note', content_type_field='content_type',
                                    object_id_field='object_id', verbose_name=_('list of notes'))

    expires = models.DateField(verbose_name=_('expires'), default=datetime.today)

    parcel = models.ForeignKey(Parcel, verbose_name=_('parcel'), null=True, blank=True)

    def __unicode__(self):
        return self.subject

    class Meta:
        verbose_name = _('case')
        verbose_name_plural = _('cases')
