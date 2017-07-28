from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from lily.tenant.models import TenantMixin


class Call(TenantMixin):
    RINGING, ANSWERED, HUNGUP = range(3)
    CALL_STATUS_CHOICES = (
        (RINGING, _('Ringing')),
        (ANSWERED, _('Answered')),
        (HUNGUP, _('Hung up')),
    )

    INBOUND, OUTBOUND = range(2)
    CALL_TYPE_CHOICES = (
        (INBOUND, _('Inbound')),
        (OUTBOUND, _('Outbound')),
    )

    # Unique id of a call as received from the telephony platform.
    unique_id = models.CharField(max_length=40)
    # Number that is being called.
    called_number = models.CharField(max_length=40)
    # Number of the caller.
    caller_number = models.CharField(max_length=40)
    # The name of the caller.
    caller_name = models.CharField(max_length=255, blank=True)
    # The internal number of the VoIP account that has answered the call or ended the call.
    internal_number = models.CharField(max_length=5)
    status = models.PositiveSmallIntegerField(choices=CALL_STATUS_CHOICES)
    type = models.PositiveSmallIntegerField(choices=CALL_TYPE_CHOICES, default=INBOUND)
    created = models.DateTimeField(auto_now_add=True, null=True)
    notes = GenericRelation('notes.Note', content_type_field='content_type', object_id_field='object_id')

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model.
        """
        return ContentType.objects.get(app_label='calls', model='call')

    def __unicode__(self):
        return '%s: Call from %s to %s' % (self.unique_id, self.caller_number, self.called_number)
