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


class CallRecord(TenantMixin):
    RINGING, IN_PROGRESS, ENDED = range(3)
    CALL_STATUS_CHOICES = (
        (RINGING, _('Ringing')),
        (IN_PROGRESS, _('In progress')),
        (ENDED, _('Ended'))
    )

    INBOUND, OUTBOUND = range(2)
    CALL_DIRECTION_CHOICES = (
        (INBOUND, _('Inbound')),
        (OUTBOUND, _('Outbound')),
    )

    # Unique id of a call as received from the telephony platform.
    call_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Unique call id')
    )
    # The start and end time of the conversation, can be used to calculate the duration.
    start = models.DateTimeField(
        verbose_name=_('Start')
    )
    end = models.DateTimeField(
        null=True,
        verbose_name=_('End')
    )
    status = models.PositiveSmallIntegerField(
        choices=CALL_STATUS_CHOICES,
        verbose_name=_('Status'),
    )
    direction = models.PositiveSmallIntegerField(
        choices=CALL_DIRECTION_CHOICES,
        verbose_name=_('Type'),
    )
    caller = models.ForeignKey(
        to='CallParticipant',
        on_delete=models.CASCADE,
        verbose_name=_('From'),
        related_name='calls_made'
    )
    destination = models.ForeignKey(
        to='CallParticipant',
        on_delete=models.CASCADE,
        verbose_name=_('To'),
        related_name='calls_received',
        null=True  # Can be null because on ringing event you don't know who picked up the phone yet.
    )
    notes = GenericRelation(
        to='notes.Note',
        content_type_field='content_type',
        object_id_field='object_id'
    )

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model.
        """
        return ContentType.objects.get(
            app_label='calls',
            model='callrecord'
        )

    def __unicode__(self):
        return '%s: Call from %s' % (
            self.call_id,
            self.caller
        )


class CallTransfer(TenantMixin):
    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp')
    )
    call = models.ForeignKey(
        to='CallRecord',
        on_delete=models.CASCADE,
        verbose_name=_('Call'),
        related_name='transfers'
    )
    destination = models.ForeignKey(
        to='CallParticipant',
        on_delete=models.CASCADE,
        verbose_name=_('To'),
        related_name='transfers_received'
    )

    def __unicode__(self):
        return 'Transfer to %s' % (
            self.destination
        )


class CallParticipant(TenantMixin):
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Name')
    )
    number = models.CharField(
        max_length=40,
        verbose_name=_('Number')
    )
    internal_number = models.CharField(
        max_length=5,
        null=True,
        verbose_name=_('Interal number')
    )

    def __unicode__(self):
        return self.name or self.number
