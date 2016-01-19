from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer
from ..models import Deal, DealNextStep


class DealSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer()

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
            'new_business',
            'next_step',
            'next_step_date',
            'content_type',
            'is_checked',
        )


class DealNextStepSerializer(serializers.ModelSerializer):
    """
    Serializer for deal next step model.
    """
    class Meta:
        model = DealNextStep
        fields = (
            'id',
            'name',
            'date_increment',
            'position',
        )

