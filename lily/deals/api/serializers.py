from rest_framework import serializers

from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.notes.api.serializers import RelatedNoteSerializer
from lily.users.api.serializers import RelatedLilyUserSerializer
from lily.utils.api.related.mixins import RelatedSerializerMixin
from lily.utils.api.related.serializers import WritableNestedSerializer
from lily.utils.api.serializers import RelatedTagSerializer
from ..models import Deal, DealNextStep, DealWhyCustomer


class DealNextStepSerializer(serializers.ModelSerializer):
    """
    Serializer for deal next step model.
    """
    class Meta:
        model = DealNextStep
        fields = (
            'id',
            'date_increment',
            'name',
            'position',
        )


class RelatedDealNextStepSerializer(RelatedSerializerMixin, DealNextStepSerializer):
    pass


class DealWhyCustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for deal why customer model.
    """
    class Meta:
        model = DealWhyCustomer
        fields = (
            'id',
            'name',
            'position',
        )


class RelatedDealWhyCustomerSerializer(RelatedSerializerMixin, DealWhyCustomerSerializer):
    pass


class DealSerializer(WritableNestedSerializer):
    """
    Serializer for the deal model.
    """
    # Set non mutable fields.
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    content_type = ContentTypeSerializer(read_only=True)

    # Related fields.
    account = RelatedAccountSerializer(required=False, allow_null=True)
    assigned_to = RelatedLilyUserSerializer(required=False, allow_null=True, assign_only=True)
    next_step = RelatedDealNextStepSerializer(assign_only=True)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)
    notes = RelatedNoteSerializer(many=True, required=False, create_only=True)
    why_customer = RelatedDealWhyCustomerSerializer(assign_only=True)

    # Show string versions of fields.
    contacted_by_display = serializers.CharField(source='get_contacted_by_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    found_through_display = serializers.CharField(source='get_found_through_display', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)

    class Meta:
        model = Deal
        fields = (
            'id',
            'account',
            'amount_once',
            'amount_recurring',
            'assigned_to',
            'card_sent',
            'closed_date',
            'contacted_by',
            'contacted_by_display',
            'content_type',
            'created',
            'currency',
            'currency_display',
            'feedback_form_sent',
            'found_through',
            'found_through_display',
            'is_archived',
            'is_checked',
            'modified',
            'name',
            'new_business',
            'next_step',
            'next_step_date',
            'notes',
            'quote_id',
            'stage',
            'stage_display',
            'tags',
            'twitter_checked',
            'why_customer',
        )



