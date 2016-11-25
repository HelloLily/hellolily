from django.db import models
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
    # The internal number of the VoIP account that has answered the call or ended the call.
    internal_number = models.CharField(max_length=5)
    status = models.PositiveSmallIntegerField(choices=CALL_STATUS_CHOICES)
    type = models.PositiveSmallIntegerField(choices=CALL_TYPE_CHOICES, default=INBOUND)

    def __unicode__(self):
        return '%s: Call from %s to %s' % (self.unique_id, self.caller_number, self.called_number)
