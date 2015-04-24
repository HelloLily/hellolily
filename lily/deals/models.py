from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.tags.models import TaggedObjectMixin
from lily.users.models import LilyUser
from lily.tenant.models import TenantMixin
from lily.utils.models.mixins import DeletedMixin, ArchivedMixin


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

    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    account = models.ForeignKey(Account, verbose_name=_('account'), null=True, blank=False)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR',
                                verbose_name=_('currency'))
    amount_once = models.DecimalField(max_digits=19, decimal_places=2, verbose_name=_('one-time cost'), default=0)
    amount_recurring = models.DecimalField(max_digits=19, decimal_places=2, verbose_name=_('recurring costs'), default=0)
    expected_closing_date = models.DateField(verbose_name=_('expected closing date'), null=True, blank=False)
    closed_date = models.DateTimeField(verbose_name=_('closed date'), blank=True, null=True)
    stage = models.IntegerField(choices=STAGE_CHOICES, default=OPEN_STAGE, verbose_name=_('status'))
    assigned_to = models.ForeignKey(LilyUser, verbose_name=_('assigned to'), null=True)
    notes = GenericRelation('notes.Note', content_type_field='content_type',
                            object_id_field='object_id', verbose_name='list of notes')
    feedback_form_sent = models.BooleanField(default=False, verbose_name=_('feedback form sent'), choices=NO_YES_CHOICES)
    new_business = models.BooleanField(default=False, verbose_name=_('new business'), choices=NO_YES_CHOICES)

    import_id = models.CharField(max_length=100, verbose_name=_('import id'), default='', blank=True, db_index=True)
    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model
        """
        return ContentType.objects.get(app_label="deals", model="deal")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('deal')
        verbose_name_plural = _('deals')
