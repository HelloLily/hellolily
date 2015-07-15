from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from lily.accounts.api.validators import HostnameValidator

from lily.api.serializers import ContentTypeSerializer
from lily.contacts.models import Contact
from lily.socialmedia.api.serializers import SocialMediaSerializer
from lily.users.api.serializers import LilyUserSerializer
from lily.utils.api.utils import update_related_fields, create_related_fields
from lily.utils.api.serializers import (AddressSerializer, EmailAddressSerializer, PhoneNumberSerializer,
                                        RelatedModelSerializer, RelatedFieldSerializer, TagSerializer)
from lily.tags.models import Tag

from ..models import Account, Website
from ..validators import DuplicateAccountName


class WebsiteSerializer(RelatedFieldSerializer):
    id = serializers.IntegerField(required=False)
    website = serializers.CharField(required=True, max_length=255, validators=[HostnameValidator()])

    class Meta:
        model = Website
        fields = (
            'id',
            'is_primary',
            'website',
        )


class ContactForAccountSerializer(RelatedModelSerializer):
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
            'preposition',
            'salutation',
        )


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the account model.
    """
    addresses = AddressSerializer(many=True)
    assigned_to = LilyUserSerializer()
    contacts = ContactForAccountSerializer(many=True, read_only=True)
    content_type = ContentTypeSerializer(read_only=True)
    email_addresses = EmailAddressSerializer(many=True)
    flatname = serializers.CharField(read_only=True)
    name = serializers.CharField(validators=[DuplicateAccountName()])
    phone_numbers = PhoneNumberSerializer(many=True)
    social_media = SocialMediaSerializer(many=True)
    tags = TagSerializer(many=True)
    websites = WebsiteSerializer(many=True)

    class Meta:
        model = Account
        fields = (
            'id',
            'addresses',
            'assigned_to',
            'bankaccountnumber',
            'bic',
            'cocnumber',
            'company_size',
            'contacts',
            'content_type',
            'created',
            'customer_id',
            'description',
            'email_addresses',
            'flatname',
            'iban',
            'legalentity',
            'logo',
            'modified',
            'name',
            'phone_numbers',
            'status',
            'social_media',
            'tags',
            'taxnumber',
            'websites',
        )


class AccountCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the creating and updating an account.
    """
    addresses = AddressSerializer(many=True, required=False)
    # assigned_to = LilyPrimaryKeyRelatedField(queryset=LilyUser.objects, required=False)
    email_addresses = EmailAddressSerializer(many=True, required=False)
    name = serializers.CharField(validators=[DuplicateAccountName()])
    phone_numbers = PhoneNumberSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    websites = WebsiteSerializer(many=True, required=False)

    # Dict used when creating/updating the related fields of the account
    related_fields = [
        {'data_string': 'websites', 'model': 'Website'},
        {'data_string': 'email_addresses', 'model': 'EmailAddress'},
        {'data_string': 'addresses', 'model': 'Address'},
        {'data_string': 'phone_numbers', 'model': 'PhoneNumber'},
    ]

    class Meta:
        model = Account
        fields = (
            'id',
            'addresses',
            'assigned_to',
            'bankaccountnumber',
            'bic',
            'cocnumber',
            'customer_id',
            'description',
            'email_addresses',
            'iban',
            'legalentity',
            'name',
            'phone_numbers',
            'tags',
            'taxnumber',
            'websites',
        )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', {})

        # We need to pop the related fields otherwise Account's __init__ won't accept it
        related_fields_data = {
            'websites': validated_data.pop('websites', {}),
            'email_addresses': validated_data.pop('email_addresses', {}),
            'addresses': validated_data.pop('addresses', {}),
            'phone_numbers': validated_data.pop('phone_numbers', {}),
        }

        # TODO: Make sure that errors in related fields raise an error and don't save the account
        account = Account(**validated_data)
        account.save()

        # Create related fields
        create_related_fields(account, self.related_fields, related_fields_data)

        for tag in tags_data:
            # Create relationship with Tag if it's a new tag
            tag_object, created = Tag.objects.get_or_create(
                name=tag['name'],
                object_id=account.pk,
                content_type_id=ContentType.objects.get_for_model(account.__class__).id
            )

        return account

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', {})

        # Create/update/delete related fields
        update_related_fields(instance, self.related_fields, validated_data)

        # TODO: Test if changing ID's of existing objects does something
        # Example: Account has website with ID 1
        # ID 2 is given, does this update website 2 or?
        # After a bit of testing this doesn't seem to be the case, but someone else should test just in case

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        tags_to_remove = Tag.objects.filter(object_id=instance.pk)
        tags_to_remove.delete()

        for tag in tags_data:
            tag_object, created = Tag.objects.get_or_create(
                name=tag['name'],
                object_id=instance.pk,
                content_type_id=ContentType.objects.get_for_model(instance.__class__).id
            )

        instance.save()

        return instance
