from elasticutils.contrib.django import MappingType, Indexable

from lily.search.indexing import prepare_dict


class BaseMapping(MappingType, Indexable):
    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.

        The default implementation sets the default analyzer and the special
        settings related to special fields such as '_all'.
        """
        return {
            'analyzer': 'normal_analyzer',
            '_all': {
                'enabled': False,
            },
            '_source': {
                'excludes': [],
            },
            'properties': {
                'tenant': {
                    'type': 'integer',
                },
                'id': {
                    'type': 'integer',
                },
            },
        }

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """
        Converts this instance into an Elasticsearch document.

        Sets the tenant and id.

        Prepares the dict before indexing it by cleaning empty and
        duplicate values.
        """
        if obj is None:
            obj = cls.get_model().objects.get(pk=obj_id)

        doc = cls.obj_to_doc(obj)

        doc['tenant'] = obj.tenant_id
        doc['id'] = obj_id

        return prepare_dict(doc)

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        raise NotImplementedError

    @classmethod
    def has_deleted(cls):
        return True
