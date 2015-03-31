from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class ContentTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's ContentType model.
    """
    class Meta:
        model = ContentType
        fields = (
            'id',
            'app_label',
            'model',
        )
