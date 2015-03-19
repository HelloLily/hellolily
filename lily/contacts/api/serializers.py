from rest_framework import serializers

from ..models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for the contact model.
    """
    # Show string versions of fields
    phone_numbers = serializers.StringRelatedField(many=True, read_only=True)
    social_media = serializers.StringRelatedField(many=True, read_only=True)
    addresses = serializers.StringRelatedField(many=True, read_only=True)
    email_addresses = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id',
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
        )
