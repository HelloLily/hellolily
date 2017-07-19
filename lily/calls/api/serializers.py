from rest_framework import serializers

from ..models import Call


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = (
            'id',
            'unique_id',
            'called_number',
            'caller_number',
            'caller_name',
            'internal_number',
            'status',
            'type',
            'created',
        )
