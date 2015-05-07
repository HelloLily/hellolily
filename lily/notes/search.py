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
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_analyzer',
            },
            'author': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'content_type': {
                'type': 'string',
                'index_analyzer': 'keyword',
            },
            'object_id': {
                'type': 'integer',
            },
            'subject_repr': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'date': {
                'type': 'date',
            },
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
            'type': obj.type,
            'type_name': obj.get_type_display(),
            'content': obj.content,
            'author': obj.author.get_full_name(),
            'content_type': obj.content_type.name,
            'object_id': obj.object_id,
            'subject_repr': str(obj.subject),
            'date': obj.sort_by_date,
        }
