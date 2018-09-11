from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer
from ..models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the TimeLog model.
    """
    content_type = ContentTypeSerializer(read_only=True)
    date = serializers.DateTimeField(required=False)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = {
            'id': obj.user.id,
            'full_name': obj.user.full_name,
            'profile_picture': obj.user.profile_picture,
        }

        return user

    def create(self, validated_data):
        user = self.context.get('request').user

        validated_data.update({
            'user': user,
        })

        return super(TimeLogSerializer, self).create(validated_data)

    class Meta:
        model = TimeLog
        fields = (
            'id',
            'billable',
            'content',
            'content_type',
            'date',
            'gfk_content_type',
            'gfk_object_id',
            'hours_logged',
            'user',
        )
