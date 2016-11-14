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
                },
            },
            'content': {
                'type': 'string',
            },
            'content_type': {
                'type': 'string',
                'index_analyzer': 'keyword',
            },
            'date': {
                'type': 'date',
            },
            'is_pinned': {
                'type': 'boolean',
            },
            'modified': {
                'type': 'date',
            },
            'object_id': {
                'type': 'integer',
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
                'full_name': obj.author.full_name,
                'id': obj.author.id,
            },
            'content': obj.content,
            'content_type': obj.content_type.name,
            'date': obj.created,
            'is_pinned': obj.is_pinned,
            'modified': obj.modified,
            'object_id': obj.object_id,
            'subject': str(obj.subject),
            'type': obj.type,
            'type_display': obj.get_type_display(),
        }
