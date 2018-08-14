from lily.search.base_mapping import BaseMapping

from .models import Tag


class TagMapping(BaseMapping):
    model = Tag
    has_deleted_mixin = False

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(TagMapping, cls).get_mapping()
        mapping['properties'].update({
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'name_flat': {
                'type': 'string',
                'index': 'not_analyzed',
            },
            'last_used': {
                'type': 'date',
            },
            'content_type': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer'
                    },
                },
            }
        })
        return mapping

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        doc = {
            'name': obj.name,
            'name_flat': obj.name,
            'last_used': obj.last_used,
            'content_type': {
                'id': obj.content_type_id,
                'name': obj.content_type.name,
            },
        }

        return doc
