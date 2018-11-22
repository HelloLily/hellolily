import analytics
import anyjson

from channels import Group
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.fields import SanitizedHtmlCharField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.contacts.api.serializers import RelatedContactSerializer
from lily.contacts.models import Function
from lily.users.api.serializers import RelatedLilyUserSerializer, RelatedTeamSerializer
from lily.utils.api.serializers import RelatedTagSerializer
from lily.utils.request import is_external_referer

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
            'is_archived',
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
    created_by = RelatedLilyUserSerializer(read_only=True)
    content_type = ContentTypeSerializer(
        read_only=True,
        help_text='This is what the object is identified as in the back-end.',
    )

    # Related fields.
    account = RelatedAccountSerializer(
        required=False,
        allow_null=True,
        help_text='Account for which the case is being created.',
    )
    contact = RelatedContactSerializer(
        required=False,
        allow_null=True,
        help_text='Contact for which the case is being created.',
    )
    assigned_to = RelatedLilyUserSerializer(
        required=False,
        allow_null=True,
        assign_only=True,
        help_text='Person which the case is assigned to.',
    )
    assigned_to_teams = RelatedTeamSerializer(
        many=True,
        required=False,
        assign_only=True,
        help_text='List of teams the case is assigned to.',
    )
    type = RelatedCaseTypeSerializer(
        assign_only=True,
        help_text='The type of case.',
    )
    status = RelatedCaseStatusSerializer(
        assign_only=True,
        help_text='Status of the case.',
    )
    tags = RelatedTagSerializer(
        many=True,
        required=False,
        create_only=True,
        help_text='Any tags used to further categorize the case.',
    )

    description = SanitizedHtmlCharField(
        help_text='Any extra text to describe the case (supports Markdown).',
    )

    # Show string versions of fields.
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True,
        help_text='Human readable value of the case\'s priority.',
    )

    def validate(self, data):
        contact_id = data.get('contact', {})
        if isinstance(contact_id, dict):
            contact_id = contact_id.get('id')

        account_id = data.get('account', {})
        if isinstance(account_id, dict):
            account_id = account_id.get('id')

        if contact_id and account_id:
            if not Function.objects.filter(contact_id=contact_id, account_id=account_id).exists():
                raise serializers.ValidationError({'contact': _('Given contact must work at the account.')})

        # Check if we are related and if we only passed in the id, which means user just wants new reference.
        errors = {
            'account': _('Please enter an account and/or contact.'),
            'contact': _('Please enter an account and/or contact.'),
        }

        if not self.partial:
            # For POST or PUT we always want to check if either is set.
            if not (account_id or contact_id):
                raise serializers.ValidationError(errors)
        else:
            # For PATCH only check the data if both account and contact are passed.
            if ('account' in data and 'contact' in data) and not (account_id or contact_id):
                raise serializers.ValidationError(errors)

        return super(CaseSerializer, self).validate(data)

    def create(self, validated_data):
        user = self.context.get('request').user
        assigned_to = validated_data.get('assigned_to')

        validated_data.update({
            'created_by_id': user.pk,
        })

        if assigned_to:
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.dumps({
                    'event': 'case-assigned',
                }),
            })

            if assigned_to.get('id') != user.pk:
                validated_data.update({
                    'newly_assigned': True,
                })

        else:
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.dumps({
                    'event': 'case-unassigned',
                }),
            })

        instance = super(CaseSerializer, self).create(validated_data)

        # Track newly ceated accounts in segment.
        if not settings.TESTING:
            analytics.track(
                user.id,
                'case-created', {
                    'expires': instance.expires,
                    'assigned_to_id': instance.assigned_to_id if instance.assigned_to else '',
                    'creation_type': 'automatic' if is_external_referer(self.context.get('request')) else 'manual',
                },
            )

        return instance

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        status_id = validated_data.get('status', instance.status_id)
        assigned_to = validated_data.get('assigned_to')

        if assigned_to:
            assigned_to = assigned_to.get('id')

        if isinstance(status_id, dict):
            status_id = status_id.get('id')

        status = CaseStatus.objects.get(pk=status_id)

        # Automatically archive the case if the status is set to 'Closed'.
        if status.name == 'Closed' and 'is_archived' not in validated_data:
            validated_data.update({
                'is_archived': True
            })

        # Check if the case being reassigned. If so we want to notify that user.
        if assigned_to and assigned_to != user.pk:
            validated_data.update({
                'newly_assigned': True,
            })
        elif 'assigned_to' in validated_data and not assigned_to:
            # Case is unassigned, so clear newly assigned flag.
            validated_data.update({
                'newly_assigned': False,
            })

        if (('status' in validated_data and status.name == 'Open') or
                ('is_archived' in validated_data and not validated_data.get('is_archived'))):
            # Case is reopened or unarchived, so we want to notify the user again.
            validated_data.update({
                'newly_assigned': True,
            })

        if 'assigned_to' in validated_data or instance.assigned_to_id:
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.serialize({
                    'event': 'case-assigned',
                }),
            })

        if (not instance.assigned_to_id or
                instance.assigned_to_id and
                'assigned_to' in validated_data and
                not validated_data.get('assigned_to')):
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.serialize({
                    'event': 'case-unassigned',
                }),
            })

        return super(CaseSerializer, self).update(instance, validated_data)

    class Meta:
        model = Case
        fields = (
            'id',
            'account',
            'assigned_to',
            'assigned_to_teams',
            'contact',
            'content_type',
            'created',
            'created_by',
            'description',
            'expires',
            'is_archived',
            'modified',
            'newly_assigned',
            'priority',
            'priority_display',
            'status',
            'tags',
            'subject',
            'type',
        )
        extra_kwargs = {
            'created': {
                'help_text': 'Shows the date and time when the deal was created.',
            },
            'expires': {
                'help_text': 'Shows the date and time for when the case should be completed.',
            },
            'modified': {
                'help_text': 'Shows the date and time when the case was last modified.',
            },
            'newly_assigned': {
                'help_text': 'True if the assignee was changed and that person hasn\'t accepted yet.',
            },
            'subject': {
                'help_text': 'A short description of the case.',
            },
        }


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
            'assigned_to_teams',
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
