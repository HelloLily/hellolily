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
    Serializer for the contact model.
    """

    class Meta:
        model = LilyUser
        fields = (
            'id',
            'first_name',
            'preposition',
            'last_name',
        )
