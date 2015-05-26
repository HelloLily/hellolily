from rest_framework import serializers

from lily.api.fields import LilyPrimaryKeyRelatedField
from lily.api.serializers import ContentTypeSerializer
from lily.contacts.models import Contact
from lily.socialmedia.api.serializers import SocialMediaSerializer
from lily.tags.api.serializers import TagSerializer
from lily.users.api.serializers import LilyUserSerializer
from lily.users.models import LilyUser
from lily.utils.api.serializers import AddressSerializer, EmailAddressSerializer, PhoneNumberSerializer, RelatedModelSerializer

from ..models import Account, Website
from ..validators import duplicate_account_name


class WebsiteSerializer(RelatedModelSerializer):

    def create(self, validated_data):
        ModelClass = self.Meta.model
        validated_data['account_id'] = self.related_object.pk
        instance = ModelClass.objects.create(**validated_data)
        return instance

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
    name = serializers.CharField(validators=[duplicate_account_name])
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

    assigned_to = LilyPrimaryKeyRelatedField(queryset=LilyUser.objects)
    name = serializers.CharField(validators=[duplicate_account_name])

    class Meta:
        model = Account
        fields = (
            'id',
            'assigned_to',
            'bankaccountnumber',
            'bic',
            'cocnumber',
            'customer_id',
            'description',
            'iban',
            'legalentity',
            'taxnumber',
            'name',
        )
