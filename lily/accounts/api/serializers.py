from rest_framework import serializers

from lily.api.fields import LilyPrimaryKeyRelatedField
from lily.api.serializers import ContentTypeSerializer
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
        fields = ('id', 'website', 'is_primary',)


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the account model.
    """
    name = serializers.CharField(validators=[duplicate_account_name])
    phone_numbers = PhoneNumberSerializer(many=True)
    social_media = SocialMediaSerializer(many=True)
    addresses = AddressSerializer(many=True)
    email_addresses = EmailAddressSerializer(many=True)
    websites = WebsiteSerializer(many=True)
    content_type = ContentTypeSerializer(read_only=True)
    assigned_to = LilyUserSerializer()
    flatname = serializers.CharField(read_only=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'phone_numbers',
            'social_media',
            'addresses',
            'email_addresses',
            'websites',
            'content_type',
            'assigned_to',
            'flatname',
            'tags',
            'created',
            'modified',
            'customer_id',
            'status',
            'company_size',
            'logo',
            'description',
            'legalentity',
            'taxnumber',
            'bankaccountnumber',
            'cocnumber',
            'iban',
            'bic',
            )


class AccountCreateSerializer(serializers.ModelSerializer):

    name = serializers.CharField(validators=[duplicate_account_name])
    assigned_to = LilyPrimaryKeyRelatedField(queryset=LilyUser.objects)

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'assigned_to',
            'customer_id',
            'description',
            'legalentity',
            'taxnumber',
            'bankaccountnumber',
            'cocnumber',
            'iban',
            'bic',
            )
