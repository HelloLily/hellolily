from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.contacts.api.serializers import RelatedContactSerializer
from lily.contacts.models import Function
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
    created_by = RelatedLilyUserSerializer(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    content_type = ContentTypeSerializer(read_only=True)

    # Related fields.
    account = RelatedAccountSerializer()
    contact = RelatedContactSerializer(required=False, allow_null=True)
    assigned_to = RelatedLilyUserSerializer(required=True, assign_only=True)
    next_step = RelatedDealNextStepSerializer(assign_only=True)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)
    notes = RelatedNoteSerializer(many=True, required=False, create_only=True)
    why_customer = RelatedDealWhyCustomerSerializer(assign_only=True)

    # Show string versions of fields.
    contacted_by_display = serializers.CharField(source='get_contacted_by_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    found_through_display = serializers.CharField(source='get_found_through_display', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)

    def validate(self, attrs):
        contact_id = attrs.get('contact', {})
        if isinstance(contact_id, dict):
            contact_id = contact_id.get('id')

        account_id = attrs.get('account', {})
        if isinstance(account_id, dict):
            account_id = account_id.get('id')

        if contact_id and account_id:
            if not Function.objects.filter(contact_id=contact_id, account_id=account_id).exists():
                raise serializers.ValidationError({'contact': _('Given contact must work at the account.')})

        return super(DealSerializer, self).validate(attrs)

    def create(self, validated_data):
        user = self.context.get('request').user

        validated_data.update({
            'created_by_id': user.pk
        })

        return super(DealSerializer, self).create(validated_data)

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
            'contact',
            'contacted_by',
            'contacted_by_display',
            'content_type',
            'created',
            'created_by',
            'currency',
            'currency_display',
            'description',
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
