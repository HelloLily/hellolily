from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.fields import empty


class ContentTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's ContentType model.
    """
    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.update({
            'read_only': True,  # This serializer must always be read only.
        })

        super(ContentTypeSerializer, self).__init__(instance=instance, data=data, **kwargs)

    class Meta:
        model = ContentType
        fields = (
            'id',
            'app_label',
            'model',
        )
