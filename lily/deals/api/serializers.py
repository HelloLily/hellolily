from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer
from ..models import Deal


class DealSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)

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
            'expected_closing_date',
            'new_business',
            'content_type',
            'is_checked',
        )
