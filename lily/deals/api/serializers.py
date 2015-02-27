from rest_framework import serializers

from ..models import Deal


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = (
            'id',
            'created',
            'deleted',
            'is_archived',
            'stage',
            'assigned_to',
            'feedback_form_sent',
            'new_business'
        )
