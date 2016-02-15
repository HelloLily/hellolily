from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.parcels.models import Parcel
from lily.tags.models import TaggedObjectMixin
from lily.tenant.models import TenantMixin
from lily.users.models import LilyGroup, LilyUser
from lily.utils.date_time import week_from_now
from lily.utils.models.mixins import DeletedMixin, ArchivedMixin


class CaseType(TenantMixin, ArchivedMixin):
    type = models.CharField(max_length=255, db_index=True)
    # Whether it shows in the filter list or not.
    use_as_filter = models.BooleanField(default=True)

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

    priority = models.SmallIntegerField(choices=PRIORITY_CHOICES, default=LOW_PRIO, verbose_name=_('priority'))
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    status = models.ForeignKey(CaseStatus, verbose_name=_('status'), related_name='cases')

    type = models.ForeignKey(CaseType, verbose_name=_('type'), null=True,
                             blank=True, related_name='cases')

    assigned_to_groups = models.ManyToManyField(
        LilyGroup,
        verbose_name=_('assigned to teams'),
        related_name='assigned_to_groups',
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(LilyUser, verbose_name=_('assigned to'),
                                    related_name='assigned_cases', null=True, blank=True)
    created_by = models.ForeignKey(LilyUser, verbose_name=_('created by'),
                                   related_name='created_cases', null=True, blank=True)

    account = models.ForeignKey(Account, verbose_name=_('account'), null=True, blank=True)
    contact = models.ForeignKey(Contact, verbose_name=_('contact'), null=True, blank=True)

    notes = GenericRelation('notes.Note', content_type_field='content_type',
                            object_id_field='object_id',
                            verbose_name=_('list of notes'))

    expires = models.DateField(verbose_name=_('expires'), default=week_from_now)

    parcel = models.ForeignKey(Parcel, verbose_name=_('parcel'), null=True, blank=True)
    billing_checked = models.BooleanField(default=False)

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model.
        """
        return ContentType.objects.get(app_label='cases', model='case')

    def __unicode__(self):
        return self.subject

    class Meta:
        verbose_name = _('case')
        verbose_name_plural = _('cases')
