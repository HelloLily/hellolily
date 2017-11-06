from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tags.models import TaggedObjectMixin
from lily.users.models import LilyUser, Team
from lily.tenant.models import TenantMixin
from lily.utils.currencies import CURRENCIES
from lily.utils.models.mixins import DeletedMixin, ArchivedMixin


class DealNextStep(TenantMixin):
    name = models.CharField(max_length=255)
    date_increment = models.IntegerField(default=0)
    position = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class DealWhyCustomer(TenantMixin):
    name = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class DealWhyLost(TenantMixin):
    name = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class DealFoundThrough(TenantMixin):
    name = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class DealContactedBy(TenantMixin):
    name = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class DealStatus(TenantMixin):
    name = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)

    @property
    def is_won(self):
        return self.name == 'Won'

    @property
    def is_lost(self):
        return self.name == 'Lost'

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class Deal(TaggedObjectMixin, TenantMixin, DeletedMixin, ArchivedMixin):
    """
    Deal model
    """

    OPEN_STAGE, PENDING_STAGE, WON_STAGE, LOST_STAGE, CALLED_STAGE, EMAILED_STAGE = range(6)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCIES)
    amount_once = models.DecimalField(default=0, max_digits=19, decimal_places=2)
    amount_recurring = models.DecimalField(default=0, max_digits=19, decimal_places=2)
    closed_date = models.DateTimeField(blank=True, null=True)
    notes = GenericRelation('notes.Note', content_type_field='gfk_content_type', object_id_field='gfk_object_id')
    quote_id = models.CharField(max_length=255, blank=True)
    next_step_date = models.DateField(null=True, blank=True)
    import_id = models.CharField(max_length=100, default='', blank=True, db_index=True)
    imported_from = models.CharField(max_length=50, null=True, blank=True)

    # Voys specific fields.
    new_business = models.BooleanField(default=False)
    is_checked = models.BooleanField(default=False)
    twitter_checked = models.BooleanField(default=False)
    card_sent = models.BooleanField(default=False)

    # Related Fields.
    account = models.ForeignKey(Account)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_to_teams = models.ManyToManyField(Team, blank=True)
    assigned_to = models.ForeignKey(LilyUser, null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(LilyUser, related_name='created_deals', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    status = models.ForeignKey(DealStatus, related_name='deals')
    found_through = models.ForeignKey(DealFoundThrough, related_name='deals', null=True, blank=True,
                                      on_delete=models.SET_NULL)
    contacted_by = models.ForeignKey(DealContactedBy, related_name='deals', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    next_step = models.ForeignKey(DealNextStep, related_name='deals')
    why_customer = models.ForeignKey(DealWhyCustomer, related_name='deals', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    why_lost = models.ForeignKey(DealWhyLost, related_name='deals', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    newly_assigned = models.BooleanField(default=False)

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model
        """
        return ContentType.objects.get(app_label='deals', model='deal')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('deal')
        verbose_name_plural = _('deals')
