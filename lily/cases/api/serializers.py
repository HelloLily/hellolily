from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.contacts.api.serializers import RelatedContactSerializer
from lily.contacts.models import Function
from lily.users.api.serializers import RelatedLilyUserSerializer, RelatedLilyGroupSerializer
from lily.utils.api.related.mixins import RelatedSerializerMixin
from lily.utils.api.related.serializers import WritableNestedSerializer

from ..models import Case, CaseStatus, CaseType


class CaseStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for case status model.
    """
    class Meta:
        model = CaseStatus
        fields = (
            'id',
            'status',
        )


class RelatedCaseStatusSerializer(RelatedSerializerMixin, CaseStatusSerializer):
    pass


class CaseTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for case type model.
    """
    class Meta:
        model = CaseType
        fields = (
            'id',
            'type',
            'use_as_filter',
        )


class RelatedCaseTypeSerializer(RelatedSerializerMixin, CaseTypeSerializer):
    pass


class CaseSerializer(WritableNestedSerializer):
    """
    Serializer for the case model.
    """
    # Set non mutable fields.
    created = serializers.DateTimeField(read_only=True)
    created_by = RelatedLilyUserSerializer(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    content_type = ContentTypeSerializer(read_only=True)

    # Related fields.
    account = RelatedAccountSerializer(required=False, allow_null=True)
    contact = RelatedContactSerializer(required=False, allow_null=True)
    assigned_to = RelatedLilyUserSerializer(required=False, allow_null=True, assign_only=True)
    assigned_to_groups = RelatedLilyGroupSerializer(many=True, required=False, allow_null=True, assign_only=True)
    type = RelatedCaseTypeSerializer(assign_only=True)
    status = RelatedCaseStatusSerializer(assign_only=True)

    # Show string versions of fields.
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

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

        return super(CaseSerializer, self).validate(attrs)

    def create(self, validated_data):
        user = self.context.get('request').user

        validated_data.update({
            'created_by_id': user.pk
        })

        return super(CaseSerializer, self).create(validated_data)

    class Meta:
        model = Case
        fields = (
            'account',
            'assigned_to',
            'assigned_to_groups',
            'contact',
            'content_type',
            'created',
            'created_by',
            'description',
            'expires',
            'id',
            'is_archived',
            'modified',
            'priority',
            'priority_display',
            'status',
            'subject',
            'type',
        )


class RelatedCaseSerializer(RelatedSerializerMixin, CaseSerializer):
    """
    Serializer for the case model when used as a relation.
    """
    class Meta:
        model = Case
        # Override the fields because we don't want related fields in this serializer.
        fields = (
            'assigned_to',
            'assigned_to_groups',
            'created',
            'created_by',
            'description',
            'expires',
            'id',
            'is_archived',
            'modified',
            'priority',
            'priority_display',
            'subject',
        )


class CasePriorityField(serializers.RelatedField):
    """
    Field that shows the priority name and id.
    """
    def to_representation(self, value):
        return Case.PRIORITY_CHOICES[value]
