import datetime
import anyjson

from channels import Group
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
from lily.users.api.serializers import RelatedLilyUserSerializer, RelatedTeamSerializer
from lily.utils.api.serializers import RelatedTagSerializer
from lily.utils.functions import add_business_days

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
    account = RelatedAccountSerializer(required=False, allow_null=True)
    contact = RelatedContactSerializer(required=False, allow_null=True)
    assigned_to = RelatedLilyUserSerializer(required=False, allow_null=True, assign_only=True)
    assigned_to_teams = RelatedTeamSerializer(many=True, required=False, assign_only=True)
    next_step = RelatedDealNextStepSerializer(assign_only=True)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)
    why_lost = RelatedDealWhyLostSerializer(assign_only=True, allow_null=True, required=False)
    why_customer = RelatedDealWhyCustomerSerializer(assign_only=True, allow_null=True, required=False)
    found_through = RelatedDealFoundThroughSerializer(assign_only=True, allow_null=True, required=False)
    contacted_by = RelatedDealContactedBySerializer(assign_only=True, allow_null=True, required=False)
    status = RelatedDealStatusSerializer(assign_only=True)

    # Show string versions of fields.
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)

    amount_once = RegexDecimalField(max_digits=19, decimal_places=2, required=True)
    amount_recurring = RegexDecimalField(max_digits=19, decimal_places=2, required=True)

    def validate(self, data):
        new_business = data.get('new_business')
        why_customer = data.get('why_customer')
        found_through = data.get('found_through')
        contacted_by = data.get('contacted_by')

        if new_business:
            errors = {}

            if not found_through:
                errors.update({'found_through': _('This field may not be empty.')})

            if not contacted_by:
                errors.update({'contacted_by': _('This field may not be empty.')})

            if not why_customer:
                errors.update({'why_customer': _('This field may not be empty.')})

            if errors:
                raise serializers.ValidationError(errors)

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

        status_id = data.get('status', {})
        if isinstance(status_id, dict):
            status_id = status_id.get('id')

        why_lost_id = data.get('why_lost', {})
        if isinstance(why_lost_id, dict):
            why_lost_id = why_lost_id.get('id')

        if status_id:
            status = DealStatus.objects.get(pk=status_id)

            if status.is_lost and why_lost_id is None and DealWhyLost.objects.exists():
                raise serializers.ValidationError({'why_lost': _('This field may not be empty.')})

        return super(DealSerializer, self).validate(data)

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

        if assigned_to:
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.serialize({
                    'event': 'deal-assigned',
                }),
            })

            if assigned_to.get('id') != user.pk:
                validated_data.update({
                    'newly_assigned': True,
                })

        else:
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.serialize({
                    'event': 'deal-unassigned',
                }),
            })

        return super(DealSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        status_id = validated_data.get('status', instance.status_id)
        next_step = validated_data.get('next_step')

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
        if assigned_to and assigned_to != user.pk:
            validated_data.update({
                'newly_assigned': True,
            })
        elif 'assigned_to' in validated_data and not assigned_to:
            # Deal is unassigned, so clear newly assigned flag.
            validated_data.update({
                'newly_assigned': False,
            })

        if (('status' in validated_data and status.name == 'Open') or
                ('is_archived' in validated_data and not validated_data.get('is_archived'))):
            # Deal is reopened or unarchived, so we want to notify the user again.
            validated_data.update({
                'newly_assigned': True,
            })

        try:
            none_step = DealNextStep.objects.get(name='None')
        except DealNextStep.DoesNotExist:
            pass

        if next_step:
            try:
                next_step = DealNextStep.objects.get(pk=next_step.get('id'))
            except DealNextStep.DoesNotExist:
                raise serializers.ValidationError({'why_lost': _('This field may not be empty.')})
            else:
                if next_step.date_increment != 0:
                    validated_data.update({
                        'next_step_date': add_business_days(next_step.date_increment),
                    })
                elif none_step and next_step.id == none_step.id:
                    validated_data.update({
                        'next_step_date': None,
                    })

        if 'assigned_to' in validated_data or instance.assigned_to_id:
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.serialize({
                    'event': 'deal-assigned',
                }),
            })

        if (not instance.assigned_to_id or
                instance.assigned_to_id and
                'assigned_to' in validated_data and
                not validated_data.get('assigned_to')):
            Group('tenant-%s' % user.tenant.id).send({
                'text': anyjson.serialize({
                    'event': 'deal-unassigned',
                }),
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
            'assigned_to_teams',
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
            'is_deleted',
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
