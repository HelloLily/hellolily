from rest_framework import serializers

from lily.accounts.api.serializers import AccountSerializer
from lily.api.serializers import ContentTypeSerializer
from ..models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for the contact model.
    """
    # Show string versions of fields
    gender = serializers.CharField(source='get_gender_display')
    phone_numbers = serializers.StringRelatedField(many=True, read_only=True)
    social_media = serializers.StringRelatedField(many=True, read_only=True)
    addresses = serializers.StringRelatedField(many=True, read_only=True)
    email_addresses = serializers.StringRelatedField(many=True, read_only=True)
    salutation = serializers.CharField(source='get_salutation_display')
    accounts = AccountSerializer(many=True, read_only=True)
    content_type = ContentTypeSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id',
            'created',
            'modified',
            'first_name',
            'preposition',
            'last_name',
            'full_name',
            'gender',
            'title',
            'description',
            'phone_numbers',
            'social_media',
            'addresses',
            'email_addresses',
            'salutation',
            'accounts',
            'content_type',
        )
