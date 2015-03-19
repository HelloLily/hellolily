from rest_framework import serializers

from ..models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the account model.
    """
    # String versions instead of id
    phone_numbers = serializers.StringRelatedField(many=True, read_only=True)
    social_media = serializers.StringRelatedField(many=True, read_only=True)
    addresses = serializers.StringRelatedField(many=True, read_only=True)
    email_addresses = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'flatname',
            'description',
            'phone_numbers',
            'social_media',
            'addresses',
            'email_addresses',
        )
