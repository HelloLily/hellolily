from elasticutils.contrib.django import Indexable, MappingType

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.search.indexing import prepare_dict
from lily.tags.models import Tag


class CaseMapping(MappingType, Indexable):
    @classmethod
    def get_model(cls):
        return Case

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        return {
            '_all': {
                'enabled': False,
            },
            'properties': {
                'tenant': {
                    'type': 'integer',
                },
                'id': {
                    'type': 'integer',
                },
                'subject': {
                    'type': 'string',
                    'index': 'analyzed',
                    'search_analyzer': 'letter_analyzer',
                    'index_analyzer': 'letter_ngram_analyzer',
                },
                'body': {
                    'type': 'string',
                    'analyzer': 'letter_analyzer',
                },
                'client': {
                    'type': 'string',
                    'analyzer': 'letter_analyzer',
                },
                'assigned_to': {
                    'type': 'string',
                    'analyzer': 'letter_analyzer',
                },
                'priority': {
                    'type': 'integer',
                },
                'priority_name': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
                'status': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
                'tag': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
                'type': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
                'expires': {
                    'type': 'date',
                },
                'archived': {
                    'type': 'boolean',
                },
            }
        }

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
    def extract_document(cls, obj_id, obj=None):
        """
        Converts this instance into an Elasticsearch document.
        """
        if obj is None:
            obj = cls.get_model().objects.get(pk=obj_id)

        doc = {
            'tenant': obj.tenant_id,
            'id': obj.id,
            'subject': obj.subject,
            'body': obj.description,
            'account': obj.account_id if obj.account else None,
            'account_name': obj.account.name if obj.account else None,
            'contact': obj.contact_id if obj.contact else None,
            'contact_name': obj.contact.full_name() if obj.contact else None,
            'assigned_to': obj.assigned_to.get_full_name() if obj.assigned_to else None,
            'priority': obj.priority,
            'priority_name': Case.PRIORITY_CHOICES[obj.priority][1],
            'status': obj.status.status,
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'type': obj.type.type if obj.type else None,
            'expires': obj.expires,
            'archived': obj.is_archived,
        }

        return prepare_dict(doc)
