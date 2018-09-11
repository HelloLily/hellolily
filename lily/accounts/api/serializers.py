import analytics
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lily.api.fields import SanitizedHtmlCharField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.api.mixins import PhoneNumberFormatMixin
from lily.contacts.models import Contact
from lily.utils.functions import clean_website
from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer
from lily.socialmedia.api.serializers import RelatedSocialMediaSerializer
from lily.users.api.serializers import RelatedLilyUserSerializer
from lily.utils.api.serializers import (RelatedAddressSerializer, RelatedEmailAddressSerializer,
                                        RelatedPhoneNumberSerializer, RelatedTagSerializer)
from lily.utils.request import is_external_referer


from ..models import Account, Website, AccountStatus
from .validators import DuplicateAccountName, HostnameValidator


class WebsiteSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=True, max_length=255, validators=[HostnameValidator()])

    def validate_website(self, value):
        return clean_website(value)

    class Meta:
        model = Website
        fields = (
            'id',
            'is_primary',
            'website',
        )


class RelatedWebsiteSerializer(RelatedSerializerMixin, WebsiteSerializer):
    pass


class ContactForAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model related to Accounts.
    This serializer is a small subset for the related Contact model.
    """
    class Meta:
        model = Contact
        fields = (
            'id',
            'first_name',
            'full_name',
            'gender',
            'last_name',
            'salutation',
        )


class AccountStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for account status model.
    """
    class Meta:
        model = AccountStatus
        fields = (
            'id',
            'name',
            'position',
        )


class RelatedAccountStatusSerializer(RelatedSerializerMixin, AccountStatusSerializer):
    pass


class AccountSerializer(PhoneNumberFormatMixin, WritableNestedSerializer):
    """
    Serializer for the account model.
    """
    # Read only fields.
    content_type = ContentTypeSerializer(
        read_only=True,
        help_text='This is what the object is identified as in the back-end.'
    )
    contacts = ContactForAccountSerializer(
        many=True,
        read_only=True,
        help_text='Contains all contacts which work for this account.',
    )

    # Related fields
    addresses = RelatedAddressSerializer(
        many=True,
        required=False,
        create_only=True,
        help_text='Addresses belonging to the account.',
    )
    assigned_to = RelatedLilyUserSerializer(
        required=False,
        allow_null=True,
        assign_only=True,
        help_text='Person which the account is assigned to.',
    )
    email_addresses = RelatedEmailAddressSerializer(
        many=True,
        required=False,
        create_only=True,
        help_text='Email addresses belonging to the account.',
    )
    phone_numbers = RelatedPhoneNumberSerializer(
        many=True,
        required=False,
        create_only=True,
        help_text='Phone numbers belonging to the account.',
    )
    social_media = RelatedSocialMediaSerializer(
        many=True,
        required=False,
        create_only=True,
        help_text='Social media accounts belonging to the account.',
    )
    websites = RelatedWebsiteSerializer(
        many=True,
        required=False,
        create_only=True,
        help_text='Any websites that belong to the account.',
    )
    status = RelatedAccountStatusSerializer(
        assign_only=True,
        help_text='ID of an AccountStatus instance.',
    )
    tags = RelatedTagSerializer(
        many=True,
        required=False,
        create_only=True,
        help_text='Any tags used to further categorize the account.',
    )

    # Custom fields.
    name = serializers.CharField(
        validators=[DuplicateAccountName()],
        help_text='The name of the account.',
    )
    description = SanitizedHtmlCharField(
        help_text='Any extra text to describe the account (supports Markdown).',
    )

    primary_email = RelatedEmailAddressSerializer(read_only=True)
    phone_number = RelatedPhoneNumberSerializer(read_only=True)

    def create(self, validated_data):
        tenant = self.context.get('request').user.tenant
        account_count = Account.objects.filter(is_deleted=False).count()

        if tenant.billing.is_free_plan and account_count >= settings.FREE_PLAN_ACCOUNT_CONTACT_LIMIT:
            raise serializers.ValidationError({
                'limit_reached': _('You\'ve reached the limit of accounts for the free plan.'),
            })

        instance = super(AccountSerializer, self).create(validated_data)

        # Track newly ceated accounts in segment.
        if not settings.TESTING:
            analytics.track(
                self.context.get('request').user.id,
                'account-created', {
                    'assigned_to_id': instance.assigned_to.id if instance.assigned_to else '',
                    'creation_type': 'automatic' if is_external_referer(self.context.get('request')) else 'manual',
                },
            )

        return instance

    class Meta:
        model = Account
        fields = (
            'id',
            'addresses',
            'assigned_to',
            'contacts',
            'content_type',
            'created',
            'customer_id',
            'description',
            'email_addresses',
            'is_deleted',
            'modified',
            'name',
            'phone_numbers',
            'social_media',
            'status',
            'tags',
            'websites',
            'primary_email',
            'phone_number',
        )
        read_only_fields = ('is_deleted', )
        extra_kwargs = {
            'created': {
                'help_text': 'Shows the date and time when the account was created.',
            },
            'modified': {
                'help_text': 'Shows the date and time when the account was last modified.',
            },
            'customer_id': {
                'help_text': 'An extra identifier for the account which can be used to link to an external source.',
            },
        }


class RelatedAccountSerializer(RelatedSerializerMixin, AccountSerializer):
    """
    Serializer for the account model when used as a relation.
    """
    class Meta:
        model = Account
        fields = (  # No related fields in this serializer.
            'id',
            'addresses',
            'created',
            'customer_id',
            'description',
            'modified',
            'name',
            'status',
            'taxnumber',
            'email_addresses',
            'phone_numbers',
            'is_deleted',
            'primary_email',
            # 'bankaccountnumber',
            # 'company_size',
            # 'bic',
            # 'cocnumber',
            # 'iban',
            # 'legalentity',
        )
        read_only_fields = ('is_deleted', )
