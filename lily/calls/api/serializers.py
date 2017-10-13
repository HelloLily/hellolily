from django.utils.timezone import now
from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer
from lily.voipgrid.api.serializers import CallNotificationSerializer

from ..models import Call, CallRecord, CallParticipant, CallTransfer


class CallSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)

    def create(self, validated_data):
        """
        For backwards compatibility this serializer temporarily saves callrecords before it is removed.
        """
        # Use the save_participant from the notification serializer because it tries to find smart names.
        # Smart names are based upon users/account/contact information.
        call_notification_serializer = CallNotificationSerializer()

        caller = call_notification_serializer.save_participant(data={
            'name': validated_data.get('caller_name'),
            'number': validated_data.get('caller_number'),
            'user_numbers': []
        })

        destination = call_notification_serializer.save_participant(data={
            'name': '',
            'number': validated_data.get('called_number'),
            'user_numbers': [validated_data.get('internal_number', None), ]
        })

        CallRecord.objects.create(
            call_id=validated_data.get('unique_id'),
            start=now(),
            end=None,
            status=CallRecord.ENDED,
            direction=CallRecord.INBOUND,
            caller=caller,
            destination=destination,
        )

        return Call()

    class Meta:
        model = Call
        fields = (
            'id',
            'unique_id',
            'called_number',
            'caller_number',
            'caller_name',
            'content_type',
            'internal_number',
            'status',
            'type',
            'created',
        )


class CallParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallParticipant
        fields = (
            'id',
            'name',
            'number',
            'internal_number',
        )


class CallTransferSerializer(serializers.ModelSerializer):
    destination = CallParticipantSerializer()

    class Meta:
        model = CallTransfer
        fields = (
            'id',
            'timestamp',
            'destination',
            'call',
        )


class CallRecordSerializer(serializers.ModelSerializer):
    caller = CallParticipantSerializer()
    destination = CallParticipantSerializer()
    transfers = CallTransferSerializer(many=True)
    content_type = ContentTypeSerializer(read_only=True)

    duration = serializers.SerializerMethodField()

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)

    def get_duration(self, obj):
        if obj.status == CallRecord.IN_PROGRESS:
            return str(now() - obj.start)

        if obj.end:
            return str(obj.end - obj.start)

        return ''

    class Meta:
        model = CallRecord
        fields = (
            'id',
            'call_id',
            'start',
            'end',
            'duration',
            'status',
            'status_display',
            'direction',
            'direction_display',
            'caller',
            'destination',
            'transfers',
            'content_type',
        )
