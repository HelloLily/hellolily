from lily.search.base_mapping import BaseMapping

from .models import Tag


class TagMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return Tag

    @classmethod
    def has_deleted(cls):
        return False

    @classmethod
    def prepare_batch(cls, queryset):
        return queryset

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
        }

        return doc
