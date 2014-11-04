from elasticutils.contrib.django import Indexable, MappingType

from lily.contacts.models import Contact


class ContactMapping(MappingType, Indexable):
    @classmethod
    def get_model(cls):
        return Contact

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        return {
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string', 'index': 'analyzed',
                         'search_analyzer': 'name_search_analyzer',
                         'index_analyzer': 'name_index_analyzer'},
                'tenant': {'type': 'integer'},
                'modified': {'type': 'date'},
            }
        }

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """
        Converts this instance into an Elasticsearch document.
        """
        if obj is None:
            obj = cls.get_model().objects.get(pk=obj_id)

        return {
            'id': obj.id,
            'name': '%s %s' % (obj.first_name, obj.last_name),
            'tenant': obj.tenant_id,
            'modified': obj.modified,
        }
