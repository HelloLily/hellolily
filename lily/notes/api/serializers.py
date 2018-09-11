from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from lily.api.fields import SanitizedHtmlCharField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.serializers import ContentTypeSerializer
from ..models import Note, NOTABLE_MODELS


class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the note model.
    """
    # Show string versions of fields.
    content_type = ContentTypeSerializer(read_only=True)
    author = serializers.SerializerMethodField()
    gfk_content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.filter(model__in=NOTABLE_MODELS),
        write_only=True,
        help_text='Content type of the object the note is linked to.',
    )
    gfk_object_id = serializers.IntegerField(
        write_only=True,
        help_text='ID of the object the note is linked to.',
    )
    content = SanitizedHtmlCharField(
        required=True,
        help_text='The actual contents of the note (supports Markdown).',
    )

    def create(self, validated_data):
        user = self.context.get('request').user

        validated_data.update({
            'author_id': user.pk,
        })

        return super(NoteSerializer, self).create(validated_data)

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'full_name': obj.author.full_name,
            'profile_picture': obj.author.profile_picture,
        }

    class Meta:
        model = Note
        fields = (
            'id',
            'author',
            'content',
            'content_type',
            'created',
            'gfk_content_type',
            'gfk_object_id',
            'is_pinned',
            'modified',
            'type',
        )
        extra_kwargs = {
            'is_pinned': {
                'help_text': 'If true the note will show at the top of the activity stream.',
            },
        }


class RelatedNoteSerializer(RelatedSerializerMixin, NoteSerializer):
    """
    Serializer used to serialize notes from reference of another serializer.
    """
    # We set required to False because, as a related serializer, we don't know the object_id yet during validation
    # of a POST request. The instance has not yet been created.
    gfk_object_id = serializers.IntegerField(required=False)

    class Meta:
        model = Note
        fields = (
            'id',
            'author',
            'content',
            'content_type',
            'created',
            'gfk_content_type',
            'gfk_object_id',
            'is_pinned',
            'modified',
            'type',
        )
