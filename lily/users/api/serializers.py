from rest_framework import serializers

from ..models import LilyGroup


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
