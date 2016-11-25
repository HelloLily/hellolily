from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from lily.api.fields import SanitizedHtmlCharField
from lily.api.nested.mixins import RelatedSerializerMixin
from ..models import Note, NOTABLE_MODELS


class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the contact model.
    """
    # Show string versions of fields.
    author = serializers.StringRelatedField(read_only=True)
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.filter(model__in=NOTABLE_MODELS),
                                                      write_only=True)
    object_id = serializers.IntegerField(write_only=True)
    content = SanitizedHtmlCharField()

    def create(self, validated_data):
        user = self.context.get('request').user

        validated_data.update({
            'author_id': user.pk,
        })

        return super(NoteSerializer, self).create(validated_data)

    class Meta:
        model = Note
        fields = (
            'id',
            'author',
            'content',
            'content_type',
            'created',
            'is_pinned',
            'modified',
            'object_id',
            'type',
        )


class RelatedNoteSerializer(RelatedSerializerMixin, NoteSerializer):
    """
    Serializer used to serialize tags from reference of another serializer.
    """
    # We set required to False because, as a related serializer, we don't know the object_id yet during validation
    # of a POST request. The instance has not yet been created.
    object_id = serializers.IntegerField(required=False)

    class Meta:
        model = Note
        fields = (
            'id',
            'author',
            'content',
            'content_type',
            'created',
            'is_pinned',
            'modified',
            'object_id',
            'type',
        )
