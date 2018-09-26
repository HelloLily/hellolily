from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer
from ..models import ObjectFile


class ObjectFileSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)

    def create(self, validated_data):
        user = self.context.get('request').user

        validated_data.update({
            'user': user,
        })

        return super(ObjectFileSerializer, self).create(validated_data)

    class Meta:
        model = ObjectFile
        fields = (
            'id',
            'file',
            'content_type',
            'size',
            'date',
            'gfk_content_type',
            'gfk_object_id',
            'user',
            'name',
        )
