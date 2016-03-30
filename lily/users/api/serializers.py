from rest_framework import serializers

from lily.utils.api.related.mixins import RelatedSerializerMixin
from ..models import LilyGroup, LilyUser


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
            'position',
            'profile_picture',
        )


class RelatedLilyUserSerializer(RelatedSerializerMixin, LilyUserSerializer):
    class Meta:
        model = LilyUser
        fields = (
            'id',
            'first_name',
            'preposition',
            'last_name',
            'full_name',
        )


class LilyGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the contact model.
    """
    user_set = RelatedLilyUserSerializer(many=True, read_only=True)

    class Meta:
        model = LilyGroup
        fields = (
            'id',
            'name',
            'user_set',
        )


class RelatedLilyGroupSerializer(RelatedSerializerMixin, LilyGroupSerializer):
    class Meta:
        model = LilyGroup
        fields = (
            'id',
            'name',
        )


class LilyUserTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for the LilyUser model.

    Only returns the user token
    """
    auth_token = serializers.CharField(read_only=True)

    class Meta:
        model = LilyUser
        fields = ('auth_token',)
