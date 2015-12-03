from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
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

    NO_YES_CHOICES = (
        (False, _('No')),
        (True, _('Yes')),
    )

    BUSINESS_CHOICES = (
        (False, _('Existing')),
        (True, _('New')),
    )

    FEEDBACK_CHOICES = (
        (False, _('Not yet')),
        (True, _('Done')),
    )

    QUOTE_CHECKED_CHOICES = (
        (False, _('Almost')),
        (True, _('Done')),
    )

    CARD_SENT_CHOICES = (
        (False, _('Writing it now')),
        (True, _('Done')),
    )

    TWITTER_CHECKED_CHOICES = (
        (False, _('Nearly')),
        (True, _('Done')),
    )

    FOUND_THROUGH_CHOICES = (
        (0, _('Search engine')),
        (1, _('Social media')),
        (2, _('Talk with employee')),
        (3, _('Existing customer')),
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
    account = models.ForeignKey(Account, verbose_name=_('account'), null=True, blank=False)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR',
                                verbose_name=_('currency'))
    amount_once = models.DecimalField(max_digits=19, decimal_places=2, verbose_name=_('one-time cost'), default=0)
    amount_recurring = models.DecimalField(max_digits=19, decimal_places=2, verbose_name=_('recurring costs'), default=0)
    closed_date = models.DateTimeField(verbose_name=_('closed date'), blank=True, null=True)
    stage = models.IntegerField(choices=STAGE_CHOICES, default=OPEN_STAGE, verbose_name=_('status'))
    assigned_to = models.ForeignKey(LilyUser, verbose_name=_('assigned to'), null=True)
    notes = GenericRelation('notes.Note', content_type_field='content_type',
                            object_id_field='object_id', verbose_name='list of notes')
    feedback_form_sent = models.BooleanField(default=False, verbose_name=_('feedback form sent'), choices=FEEDBACK_CHOICES)
    new_business = models.BooleanField(default=False, verbose_name=_('business'), choices=BUSINESS_CHOICES)
    is_checked = models.BooleanField(default=False, verbose_name=_('quote checked'), choices=QUOTE_CHECKED_CHOICES)
    twitter_checked = models.BooleanField(default=False, choices=TWITTER_CHECKED_CHOICES)
    card_sent = models.BooleanField(default=False, choices=CARD_SENT_CHOICES)
    quote_id = models.CharField(max_length=255, verbose_name=_('freedom quote id'), blank=True)
    found_through = models.IntegerField(max_length=255, blank=True, null=True, choices=FOUND_THROUGH_CHOICES, verbose_name=_('found us through'))
    contacted_by = models.IntegerField(max_length=255, blank=True, null=True, choices=CONTACTED_BY_CHOICES, verbose_name=_('contacted us by'))
    next_step = models.ForeignKey(DealNextStep, verbose_name=_('next step'), null=True, related_name='deals')
    next_step_date = models.DateField(verbose_name=_('next step date'), null=True, blank=True)

    import_id = models.CharField(max_length=100, verbose_name=_('import id'), default='', blank=True, db_index=True)

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
