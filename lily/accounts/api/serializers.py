from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q

from lily.api.fields import LilyPrimaryKeyRelatedField
from lily.api.serializers import ContentTypeSerializer
from lily.contacts.models import Contact
from lily.socialmedia.api.serializers import SocialMediaSerializer
from lily.users.api.serializers import LilyUserSerializer
from lily.users.models import LilyUser
from lily.utils.api.serializers import (AddressSerializer, EmailAddressSerializer, PhoneNumberSerializer,
                                        RelatedModelSerializer, RelatedFieldSerializer, TagSerializer)
from lily.utils.models.models import Address, EmailAddress, PhoneNumber
from lily.tags.models import Tag

from ..models import Account, Website
from ..validators import DuplicateAccountName


class WebsiteSerializer(RelatedFieldSerializer):
    id = serializers.IntegerField(required=False)
    website = serializers.CharField(required=True, max_length=255)

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
    tags = TagSerializer(many=True)
    websites = WebsiteSerializer(many=True, required=False)

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
        websites_data = validated_data.pop('websites')
        email_addresses_data = validated_data.pop('email_addresses')
        addresses_data = validated_data.pop('addresses')
        phone_numbers_data = validated_data.pop('phone_numbers')
        tags_data = validated_data.pop('tags')

        # TODO: Make sure that errors in related fields raise an error and don't save the account
        account = Account(**validated_data)
        account.save()

        for website_data in websites_data:
            if not website_data['is_deleted']:
                del website_data['is_deleted']
                Website.objects.create(account=account, **website_data)

        for email_address_data in email_addresses_data:
            if not email_address_data['is_deleted']:
                del email_address_data['is_deleted']
                account.email_addresses.add(EmailAddress.objects.create(**email_address_data))

        for address_data in addresses_data:
            if not address_data['is_deleted']:
                del address_data['is_deleted']
                account.addresses.add(Address.objects.create(**address_data))

        for phone_number_data in phone_numbers_data:
            if not phone_number_data['is_deleted']:
                del phone_number_data['is_deleted']
                account.phone_numbers.add(PhoneNumber.objects.create(**phone_number_data))

        for tag in tags_data:
            # Create relationship with Tag if it's a new tag
            tag_object, created = Tag.objects.get_or_create(
                name=tag['name'],
                object_id=account.pk,
                content_type_id=ContentType.objects.get_for_model(account.__class__).id
            )

        return account

    def update(self, instance, validated_data):
        websites_data = validated_data.pop('websites')
        email_addresses_data = validated_data.pop('email_addresses')
        addresses_data = validated_data.pop('addresses')
        phone_numbers_data = validated_data.pop('phone_numbers')
        tags_data = validated_data.pop('tags')

        # TODO: Test if changing ID's of existing objects does something
        # Example: Account has website with ID 1
        # ID 2 is given, does this update website 2 or?
        # After a bit of testing this doesn't seem to be the case, but someone else should test just in case

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        # Do the following for the related fields:
        # 1. Convert from OrderedDict to regular dict
        # 2. Either update an existing object or create a new one
        # 3. update_or_create returns (object, created), where created is whether it's a new object or not
        # 4. If true (object[1]), add the object to the set of objects

        # TODO: LILY-964: Make generic function for this bit

        for website_data in websites_data:
            if not website_data:
                continue

            website_data_dict = dict(website_data)
            is_deleted = website_data_dict['is_deleted']

            del website_data_dict['is_deleted']

            if 'id' in website_data_dict:
                website = instance.websites.filter(pk=website_data_dict.get('id'))

                if is_deleted:
                    website.delete()
                else:
                    website.update(**website_data_dict)
            else:
                # Websites aren't added to a set, but are given an account
                website_data_dict.update({
                    'account': instance
                })
                Website.objects.create(**website_data_dict)

        for email_address_data in email_addresses_data:
            if not email_address_data:
                continue

            email_address_data_dict = dict(email_address_data)
            is_deleted = email_address_data_dict['is_deleted']

            del email_address_data_dict['is_deleted']

            if 'id' in email_address_data_dict:
                email_address = instance.email_addresses.filter(pk=email_address_data_dict['id'])

                if is_deleted:
                    email_address.delete()
                else:
                    email_address.update(**email_address_data_dict)
            else:
                instance.email_addresses.add(EmailAddress.objects.create(**email_address_data_dict))

        for address_data in addresses_data:
            if not address_data:
                continue

            address_data_dict = dict(address_data)

            is_deleted = address_data_dict['is_deleted']

            del address_data_dict['is_deleted']

            if 'id' in address_data_dict:
                address = instance.addresses.filter(pk=address_data_dict['id'])

                if is_deleted:
                    address.delete()
                else:
                    address.update(**address_data_dict)
            else:
                instance.addresses.add(Address.objects.create(**address_data_dict))

        for phone_number_data in phone_numbers_data:
            if not phone_number_data:
                continue

            phone_number_data_dict = dict(phone_number_data)

            is_deleted = phone_number_data_dict['is_deleted']

            del phone_number_data_dict['is_deleted']

            if 'id' in phone_number_data_dict:
                phone_number = instance.phone_numbers.filter(pk=phone_number_data_dict['id'])

                if is_deleted:
                    phone_number.delete()
                else:
                    phone_number.update(**phone_number_data_dict)
            else:
                instance.phone_numbers.add(PhoneNumber.objects.create(**phone_number_data_dict))

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
