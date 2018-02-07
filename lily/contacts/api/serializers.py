from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.fields import SanitizedHtmlCharField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.api.mixins import PhoneNumberFormatMixin
from lily.api.serializers import ContentTypeSerializer
from lily.integrations.credentials import get_credentials
from lily.socialmedia.api.serializers import RelatedSocialMediaSerializer
from lily.utils.api.serializers import (RelatedPhoneNumberSerializer, RelatedAddressSerializer,
                                        RelatedEmailAddressSerializer, RelatedTagSerializer)
from lily.utils.functions import send_get_request, send_post_request, has_required_tier

from ..models import Contact, Function


class FunctionSerializer(serializers.ModelSerializer):
    account_name = serializers.SerializerMethodField()

    def get_account_name(self, obj):
        return obj.account.name

    class Meta:
        model = Function
        fields = (
            'id',
            'account',
            'account_name',
            'is_active',
        )


class RelatedFunctionSerializer(RelatedSerializerMixin, FunctionSerializer):
    pass


class ContactSerializer(PhoneNumberFormatMixin, WritableNestedSerializer):
    """
    Serializer for the contact model.
    """
    # Custom fields.
    description = SanitizedHtmlCharField()

    # Set non mutable fields.
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    content_type = ContentTypeSerializer(read_only=True)

    # Related fields.
    phone_numbers = RelatedPhoneNumberSerializer(many=True, required=False, create_only=True)
    addresses = RelatedAddressSerializer(many=True, required=False, create_only=True)
    email_addresses = RelatedEmailAddressSerializer(many=True, required=False, create_only=True)
    social_media = RelatedSocialMediaSerializer(many=True, required=False, create_only=True)
    accounts = RelatedAccountSerializer(many=True, required=False)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)
    functions = RelatedFunctionSerializer(many=True, required=False, create_only=True)

    # Show string versions of fields.
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    salutation_display = serializers.CharField(source='get_salutation_display', read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id',
            'accounts',
            'addresses',
            'content_type',
            'created',
            'description',
            'email_addresses',
            'first_name',
            'full_name',
            'gender',
            'gender_display',
            'is_deleted',
            'last_name',
            'modified',
            'phone_numbers',
            'salutation',
            'salutation_display',
            'social_media',
            'tags',
            'title',
            'functions',
        )
        read_only_fields = ('is_deleted', )

    def validate(self, data):
        if not isinstance(data, dict):
            data = {'id': data}

        # Check if we are related and if we only passed in the id, which means user just wants new reference.
        if not (len(data) == 1 and 'id' in data and hasattr(self, 'is_related_serializer')):
            errors = {
                'first_name': _('Please enter a valid first name.'),
                'last_name': _('Please enter a valid last name.')
            }

            if not self.partial:
                first_name = data.get('first_name', None)
                last_name = data.get('last_name', None)

                # Not just a new reference, so validate if contact is set properly.
                if not any([first_name, last_name]):
                    raise serializers.ValidationError(errors)
            else:
                if 'first_name' in data and 'last_name' in data:
                    first_name = data.get('first_name', None)
                    last_name = data.get('last_name', None)

                    if not (first_name or last_name):
                        raise serializers.ValidationError(errors)

        return super(ContactSerializer, self).validate(data)

    def create(self, validated_data):
        tenant = self.context.get('request').user.tenant
        contact_count = Contact.objects.filter(is_deleted=False).count()

        if tenant.billing.is_free_plan and contact_count >= settings.FREE_PLAN_ACCOUNT_CONTACT_LIMIT:
            raise serializers.ValidationError({
                'limit_reached': _('You\'ve reached the limit of contacts for the free plan.'),
            })

        instance = super(ContactSerializer, self).create(validated_data)

        credentials = get_credentials('moneybird')

        if has_required_tier(2) and credentials and credentials.integration_context.get('auto_sync'):
            self.send_moneybird_contact(validated_data, instance, credentials)

        return instance

    def update(self, instance, validated_data):
        # Save the current data for later use.
        original_data = {
            'full_name': instance.full_name,
        }

        email_addresses = instance.email_addresses.all()

        if len(email_addresses) == 1:
            original_data.update({
                'original_email_address': email_addresses[0].email_address
            })

        instance = super(ContactSerializer, self).update(instance, validated_data)

        credentials = get_credentials('moneybird')

        if has_required_tier(2) and credentials and credentials.integration_context.get('auto_sync'):
            self.send_moneybird_contact(validated_data, instance, credentials, original_data)

        return instance

    def send_moneybird_contact(self, validated_data, instance, credentials, original_data=None):
        administration_id = credentials.integration_context.get('administration_id')
        contact_url = 'https://moneybird.com/api/v2/%s/contacts'

        if original_data:
            full_name = original_data.get('full_name')
        else:
            full_name = instance.full_name

        search_url = (contact_url + '?query=%s') % (administration_id, full_name)
        response = send_get_request(search_url, credentials)
        data = response.json()

        patch = False
        params = {}

        if data:
            data = data[0]
            moneybird_id = data.get('id')
            post_url = (contact_url + '/%s') % (administration_id, moneybird_id)

            params = {
                'id': moneybird_id,
            }

            # Existing Moneybird contact found so we want to PATCH.
            patch = True
        else:
            post_url = contact_url % administration_id

        if 'first_name' in validated_data:
            params.update({'firstname': validated_data.get('first_name')})

        if 'last_name' in validated_data:
            params.update({'lastname': validated_data.get('last_name')})

        accounts = instance.accounts.all()

        if 'accounts' in validated_data and len(accounts) == 1:
            params.update({'company_name': accounts[0].name})

        if 'phone_numbers' in validated_data:
            phone_numbers = []

            for validated_number in validated_data.get('phone_numbers'):
                for phone_number in instance.phone_numbers.all():
                    if validated_number.get('number') == phone_number.number:
                        phone_numbers.append(phone_number)
                        break

            if phone_numbers:
                params.update({'phone': phone_numbers[0].number})

        if 'addresses' in validated_data:
            addresses = []

            for validated_address in validated_data.get('addresses'):
                for address in instance.addresses.all():
                    if validated_address.get('address') == address.address:
                        addresses.append(address)
                        break

            if addresses:
                address = addresses[0]
                params.update({
                    'address1': address.address,
                    'zipcode': address.postal_code,
                    'city': address.city,
                    'country': address.country,
                })

        if 'email_addresses' in validated_data:
            original_email_address = None
            validated_email_addresses = validated_data.get('email_addresses')

            if original_data:
                original_email_address = original_data.get('original_email_address')

            if len(validated_email_addresses) == 1:
                validated_email_address = validated_email_addresses[0].get('email_address')

                if data and original_email_address:
                    invoices_email = data.get('send_invoices_to_email')
                    estimates_email = data.get('send_estimates_to_email')

                    if invoices_email == estimates_email and invoices_email == original_email_address:
                        params.update({
                            'send_invoices_to_email': validated_email_address,
                            'send_estimates_to_email': validated_email_address,
                        })
                    elif invoices_email == original_email_address:
                        params.update({
                            'send_invoices_to_email': validated_email_address,
                        })
                    elif estimates_email == original_email_address:
                        params.update({
                            'send_estimates_to_email': validated_email_address,
                        })
                else:
                    params.update({
                        'send_invoices_to_email': validated_email_address,
                        'send_estimates_to_email': validated_email_address,
                    })

        params = {
            'contact': params,
            'administration_id': administration_id
        }

        response = send_post_request(post_url, credentials, params, patch, True)


class RelatedContactSerializer(RelatedSerializerMixin, ContactSerializer):
    """
    Serializer for the contact model when used as a relation.
    """
    class Meta:
        model = Contact
        # Override the fields because we don't want related fields in this serializer.
        fields = (
            'id',
            'created',
            'modified',
            'first_name',
            'last_name',
            'full_name',
            'gender',
            'gender_display',
            'title',
            'description',
            'salutation',
            'salutation_display',
            'is_deleted',
            'functions',
        )
        read_only_fields = ('is_deleted', )
