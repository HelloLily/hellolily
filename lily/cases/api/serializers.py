from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.contacts.api.serializers import RelatedContactSerializer
from lily.contacts.models import Function
from lily.users.api.serializers import RelatedLilyUserSerializer, RelatedLilyGroupSerializer
from lily.users.models import LilyGroup
from lily.utils.api.serializers import RelatedTagSerializer

from ..models import Case, CaseStatus, CaseType


class CaseStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for case status model.
    """
    class Meta:
        model = CaseStatus
        fields = (
            'id',
            'name',
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
            'name',
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
    assigned_to_groups = RelatedLilyGroupSerializer(many=True, required=False, assign_only=True)
    type = RelatedCaseTypeSerializer(assign_only=True)
    status = RelatedCaseStatusSerializer(assign_only=True)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)

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

    def update(self, instance, validated_data):
        status_id = validated_data.get('status', instance.status_id)

        if isinstance(status_id, dict):
            status_id = status_id.get('id')

        status = CaseStatus.objects.get(pk=status_id)

        # Automatically archive the case if the status is set to 'Closed'.
        if status.name == 'Closed':
            validated_data.update({
                'is_archived': True
            })

        if self.partial:
            # Handle PATCH on assigned to groups as a special case.
            # Removed assigned_to_groups lack the is_deleted flag, so replace the whole resource.
            assigned_to_groups_validated_data = validated_data.pop('assigned_to_groups', {})
            instance.assigned_to_groups.clear()
            for group_validated in assigned_to_groups_validated_data:
                group = LilyGroup.objects.get(pk=group_validated['id'])
                if group:
                    instance.assigned_to_groups.add(group)

        return super(CaseSerializer, self).update(instance, validated_data)

    class Meta:
        model = Case
        fields = (
            'id',
            'account',
            'assigned_to',
            'assigned_to_groups',
            'contact',
            'content_type',
            'created',
            'created_by',
            'description',
            'expires',
            'is_archived',
            'modified',
            'priority',
            'priority_display',
            'status',
            'tags',
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
            'id',
            'assigned_to',
            'assigned_to_groups',
            'created',
            'created_by',
            'description',
            'expires',
            'is_archived',
            'modified',
            'priority',
            'priority_display',
            'subject',
        )
