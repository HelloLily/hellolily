from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.parcels.models import Parcel
from lily.tags.models import TaggedObjectMixin
from lily.tenant.models import TenantMixin
from lily.users.models import Team, LilyUser
from lily.utils.date_time import week_from_now
from lily.utils.models.mixins import DeletedMixin, ArchivedMixin


class CaseType(TenantMixin, ArchivedMixin):
    name = models.CharField(max_length=255, db_index=True)
    # Whether it shows in the filter list or not.
    use_as_filter = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class CaseStatus(TenantMixin):
    position = models.IntegerField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

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

    priority = models.SmallIntegerField(choices=PRIORITY_CHOICES, default=LOW_PRIO)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.ForeignKey(CaseStatus, related_name='cases')
    type = models.ForeignKey(CaseType, related_name='cases')

    assigned_to_teams = models.ManyToManyField(Team, related_name='assigned_to_teams', blank=True)
    assigned_to = models.ForeignKey(LilyUser, related_name='assigned_cases', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    created_by = models.ForeignKey(LilyUser, related_name='created_cases', null=True, blank=True,
                                   on_delete=models.SET_NULL)

    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL)

    notes = GenericRelation('notes.Note', content_type_field='gfk_content_type', object_id_field='gfk_object_id')

    expires = models.DateField(default=week_from_now)

    parcel = models.ForeignKey(Parcel, null=True, blank=True, on_delete=models.SET_NULL)
    billing_checked = models.BooleanField(default=False)
    newly_assigned = models.BooleanField(default=False)

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
