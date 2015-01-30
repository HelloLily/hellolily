from lily.accounts.models import Account
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.search.base_mapping import BaseMapping
from lily.tags.models import Tag


class CaseMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return Case

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(CaseMapping, cls).get_mapping()
        mapping.update({
            'properties': {
                'subject': {
                    'type': 'string',
                    'index_analyzer': 'normal_ngram_analyzer',
                },
                'body': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'account': {
                    'type': 'integer',
                },
                'account_name': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'contact': {
                    'type': 'integer',
                },
                'contact_name': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'assigned_to': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'priority': {
                    'type': 'integer',
                },
                'priority_name': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'status': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'tag': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'type': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'expires': {
                    'type': 'date',
                },
                'archived': {
                    'type': 'boolean',
                },
            }
        })
        return mapping

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
            Contact: lambda obj: obj.case_set.all(),
            Account: lambda obj: obj.case_set.all(),
            Tag: lambda obj: [obj.subject],
        }

    @classmethod
    def prepare_batch(cls, queryset):
        """
        Optimize a queryset for batch indexing.
        """
        return queryset.prefetch_related(
            'status',
            'type',
            'account',
            'contact',
            'assigned_to',
            'tags',
        )

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'subject': obj.subject,
            'body': obj.description,
            'account': obj.account_id if obj.account else None,
            'account_name': obj.account.name if obj.account else None,
            'contact': obj.contact_id if obj.contact else None,
            'contact_name': obj.contact.full_name() if obj.contact else None,
            'assigned_to': obj.assigned_to.get_full_name() if obj.assigned_to else None,
            'created_by': obj.created_by.get_full_name() if obj.created_by else None,
            'priority': obj.priority,
            'priority_name': Case.PRIORITY_CHOICES[obj.priority][1],
            'status': obj.status.status,
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'type': obj.type.type if obj.type else None,
            'expires': obj.expires,
            'archived': obj.is_archived,
        }
