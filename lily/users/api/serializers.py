from rest_framework import serializers

from ..models import LilyGroup, LilyUser


class LilyGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the contact model.
    """

    class Meta:
        model = LilyGroup
        fields = (
            'id',
            'name',
        )


class LilyUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the LilyUser model.
    """
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = LilyUser
        fields = (
            'id',
            'first_name',
            'preposition',
            'last_name',
            'full_name',
            'primary_email_account',
        )
