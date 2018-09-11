from lily.search.base_mapping import BaseMapping

from .models import Note


class NoteMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return Note

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """

        mapping = super(NoteMapping, cls).get_mapping()
        mapping['properties'].update({
            'author': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'profile_picture': {'type': 'string'},
                },
            },
            'content': {
                'type': 'string',
            },
            'date': {
                'type': 'date',
            },
            'gfk_content_type': {
                'type': 'string',
                'index_analyzer': 'keyword',
            },
            'gfk_object_id': {
                'type': 'integer',
            },
            'is_pinned': {
                'type': 'boolean',
            },
            'modified': {
                'type': 'date',
            },
            'subject': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'type': {
                'type': 'integer',
            },
            'type_display': {
                'type': 'string',
            }
        })
        return mapping

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
        }

    @classmethod
    def prepare_batch(cls, queryset):
        """
        Optimize a queryset for batch indexing.
        """
        return queryset

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'author': {
                'id': obj.author.id,
                'full_name': obj.author.full_name,
                'profile_picture': obj.author.profile_picture
            },
            'content': obj.content,
            'content_type': obj.content_type.id,
            'date': obj.created,
            'created': obj.created,
            'gfk_content_type': obj.gfk_content_type.model,
            'gfk_object_id': obj.gfk_object_id,
            'is_pinned': obj.is_pinned,
            'modified': obj.modified,
            'subject': str(obj.subject),
            'type': obj.type,
            'type_display': obj.get_type_display(),
        }
