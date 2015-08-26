from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from ..models import Note, NOTABLE_MODELS


class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the contact model.
    """
    # Show string versions of fields
    author = serializers.StringRelatedField(read_only=True)
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.filter(model__in=NOTABLE_MODELS))

    class Meta:
        model = Note
        fields = (
            'id',
            'created',
            'modified',
            'content',
            'author',
            'content_type',
            'object_id',
            'is_pinned',
        )
