from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tags.models import TaggedObjectMixin
from lily.users.models import LilyUser
from lily.tenant.models import TenantMixin
from lily.utils.models.mixins import DeletedMixin, ArchivedMixin


class DealNextStep(TenantMixin):
    name = models.CharField(max_length=255)
    date_increment = models.IntegerField(default=0)
    position = models.IntegerField(choices=[(i, i) for i in range(10)], default=9)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class DealWhyCustomer(TenantMixin):
    name = models.CharField(max_length=255)
    position = models.IntegerField(choices=[(i, i) for i in range(10)], default=9)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


class Deal(TaggedObjectMixin, TenantMixin, DeletedMixin, ArchivedMixin):
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

    OPEN_STAGE, PENDING_STAGE, WON_STAGE, LOST_STAGE, CALLED_STAGE, EMAILED_STAGE = range(6)
    STAGE_CHOICES = (
        (OPEN_STAGE, _('Open')),
        (PENDING_STAGE, _('Proposal sent')),
        (WON_STAGE, _('Won')),
        (LOST_STAGE, _('Lost')),
        (CALLED_STAGE, _('Called')),
        (EMAILED_STAGE, _('Emailed')),
    )

    FOUND_THROUGH_CHOICES = (
        (0, _('Search engine')),
        (1, _('Social media')),
        (2, _('Talk with employee')),
        (3, _('Existing customer')),
        (5, _('Radio')),
        (6, _('Public speaking')),
        (7, _('Press and articles')),
        (4, _('Other')),
    )

    CONTACTED_BY_CHOICES = (
        (0, _('Quote')),
        (1, _('Contact form')),
        (2, _('Phone')),
        (3, _('Web chat')),
        (4, _('E-mail')),
        (6, _('Instant connect')),
        (5, _('Other')),
    )

    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    account = models.ForeignKey(Account, verbose_name=_('account'))
    contact = models.ForeignKey(Contact, verbose_name=_('contact'), null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, verbose_name=_('currency'))
    amount_once = models.DecimalField(max_digits=19, decimal_places=2, verbose_name=_('one-time cost'))
    amount_recurring = models.DecimalField(max_digits=19, decimal_places=2, verbose_name=_('recurring costs'))
    closed_date = models.DateTimeField(verbose_name=_('closed date'), blank=True, null=True)
    stage = models.IntegerField(choices=STAGE_CHOICES, verbose_name=_('status'))
    assigned_to = models.ForeignKey(LilyUser, verbose_name=_('assigned to'), null=True)
    created_by = models.ForeignKey(LilyUser, verbose_name=_('created by'),
                                   related_name='created_deals', null=True, blank=True)
    notes = GenericRelation('notes.Note', content_type_field='content_type', object_id_field='object_id',
                            verbose_name='list of notes')
    feedback_form_sent = models.BooleanField(default=False, verbose_name=_('feedback form sent'))
    new_business = models.BooleanField(default=False, verbose_name=_('business'))
    is_checked = models.BooleanField(default=False, verbose_name=_('quote checked'))
    twitter_checked = models.BooleanField(default=False)
    card_sent = models.BooleanField(default=False)
    quote_id = models.CharField(max_length=255, verbose_name=_('freedom quote id'), blank=True)
    found_through = models.IntegerField(max_length=255, choices=FOUND_THROUGH_CHOICES,
                                        verbose_name=_('found us through'))
    contacted_by = models.IntegerField(max_length=255, choices=CONTACTED_BY_CHOICES, verbose_name=_('contacted us by'))
    next_step = models.ForeignKey(DealNextStep, verbose_name=_('next step'), related_name='deals')
    next_step_date = models.DateField(verbose_name=_('next step date'), null=True, blank=True)
    import_id = models.CharField(max_length=100, verbose_name=_('import id'), default='', blank=True, db_index=True)
    imported_from = models.CharField(max_length=50, verbose_name=_('imported from'), null=True, blank=True)
    why_customer = models.ForeignKey(DealWhyCustomer, verbose_name=_('why'), related_name='deals')

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
