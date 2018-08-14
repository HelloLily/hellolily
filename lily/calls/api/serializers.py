from django.utils.timezone import now
from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer

from ..models import Call, CallRecord, CallParticipant, CallTransfer


class CallSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)

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
            return str(now() - obj.start).split(".")[0]

        if obj.end:
            return str(obj.end - obj.start).split(".")[0]

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
