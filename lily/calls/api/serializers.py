from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer

from ..models import Call


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
