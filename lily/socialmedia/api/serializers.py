from rest_framework import serializers

from ..models import SocialMedia


# Serializer not done yet, see tags serializer for reference.
class SocialMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialMedia
