import datetime

from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from lily.api.fields import RegexDecimalField, SanitizedHtmlCharField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from rest_framework import serializers

from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.contacts.api.serializers import RelatedContactSerializer
from lily.contacts.models import Function
from lily.users.api.serializers import RelatedLilyUserSerializer
from lily.utils.api.serializers import RelatedTagSerializer

from ..models import Deal, DealNextStep, DealWhyCustomer, DealWhyLost, DealFoundThrough, DealContactedBy, DealStatus


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


class DealWhyLostSerializer(serializers.ModelSerializer):
    """
    Serializer for deal why lost model.
    """
    class Meta:
        model = DealWhyLost
        fields = (
            'id',
            'name',
            'position',
        )


class RelatedDealWhyLostSerializer(RelatedSerializerMixin, DealWhyLostSerializer):
    pass


class DealFoundThroughSerializer(serializers.ModelSerializer):
    """
    Serializer for deal found through model.
    """
    class Meta:
        model = DealFoundThrough
        fields = (
            'id',
            'name',
            'position',
        )


class RelatedDealFoundThroughSerializer(RelatedSerializerMixin, DealFoundThroughSerializer):
    pass


class DealContactedBySerializer(serializers.ModelSerializer):
    """
    Serializer for deal contacted by model.
    """
    class Meta:
        model = DealContactedBy
        fields = (
            'id',
            'name',
            'position',
        )


class RelatedDealContactedBySerializer(RelatedSerializerMixin, DealContactedBySerializer):
    pass


class DealStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for deal status model.
    """
    class Meta:
        model = DealStatus
        fields = (
            'id',
            'name',
            'position',
        )


class RelatedDealStatusSerializer(RelatedSerializerMixin, DealStatusSerializer):
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

    # Custom fields.
    description = SanitizedHtmlCharField()

    # Related fields.
    account = RelatedAccountSerializer()
    contact = RelatedContactSerializer(required=False, allow_null=True)
    assigned_to = RelatedLilyUserSerializer(required=False, allow_null=True, assign_only=True)
    next_step = RelatedDealNextStepSerializer(assign_only=True)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)
    why_customer = RelatedDealWhyCustomerSerializer(assign_only=True)
    why_lost = RelatedDealWhyLostSerializer(assign_only=True, allow_null=True, required=False)
    found_through = RelatedDealFoundThroughSerializer(assign_only=True)
    contacted_by = RelatedDealContactedBySerializer(assign_only=True)
    status = RelatedDealStatusSerializer(assign_only=True)

    # Show string versions of fields.
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)

    amount_once = RegexDecimalField(max_digits=19, decimal_places=2, required=True)
    amount_recurring = RegexDecimalField(max_digits=19, decimal_places=2, required=True)

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

        status_id = attrs.get('status', {})
        if isinstance(status_id, dict):
            status_id = status_id.get('id')

        why_lost_id = attrs.get('why_lost', {})
        if isinstance(why_lost_id, dict):
            why_lost_id = why_lost_id.get('id')

        if status_id:
            status = DealStatus.objects.get(pk=status_id)

            if status.is_lost and why_lost_id is None and DealWhyLost.objects.exists():
                raise serializers.ValidationError({'why_lost': _('This field may not be empty.')})

        return super(DealSerializer, self).validate(attrs)

    def create(self, validated_data):
        user = self.context.get('request').user
        status_id = validated_data.get('status').get('id')
        status = DealStatus.objects.get(pk=status_id)
        closed_date = validated_data.get('closed_date')

        # Set closed_date if status is lost/won and not manually provided.
        if (status.is_won or status.is_lost) and not closed_date:
            closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        else:
            closed_date = None

        validated_data.update({
            'created_by_id': user.pk,
            'closed_date': closed_date,
        })

        assigned_to = validated_data.get('assigned_to')

        if assigned_to and assigned_to.get('id') != user.pk:
            validated_data.update({
                'newly_assigned': True,
            })

        return super(DealSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        status_id = validated_data.get('status', instance.status_id)

        if isinstance(status_id, dict):
            status_id = status_id.get('id')

        status = DealStatus.objects.get(pk=status_id)
        closed_date = validated_data.get('closed_date', instance.closed_date)
        assigned_to = validated_data.get('assigned_to')

        if assigned_to:
            assigned_to = assigned_to.get('id')

        # Set closed_date after changing status to lost/won and reset it when it's any other status.
        if status.is_won or status.is_lost:
            if not closed_date:
                closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        else:
            closed_date = None

        validated_data.update({
            'closed_date': closed_date,
        })

        # Check if the deal is being reassigned. If so we want to notify that user.
        if assigned_to and assigned_to != user.pk and instance.assigned_to and instance.assigned_to.id != assigned_to:
            validated_data.update({
                'newly_assigned': True,
            })

        return super(DealSerializer, self).update(instance, validated_data)

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
            'content_type',
            'created',
            'created_by',
            'currency',
            'currency_display',
            'description',
            'found_through',
            'is_archived',
            'is_checked',
            'modified',
            'name',
            'new_business',
            'newly_assigned',
            'next_step',
            'next_step_date',
            'quote_id',
            'status',
            'tags',
            'twitter_checked',
            'why_customer',
            'why_lost',
        )
