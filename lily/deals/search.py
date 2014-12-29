from elasticutils.contrib.django import Indexable, MappingType

from lily.accounts.models import Account
from lily.deals.models import Deal
from lily.search.indexing import prepare_dict
from lily.tags.models import Tag


class DealMapping(MappingType, Indexable):
    @classmethod
    def get_model(cls):
        return Deal

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        return {
            'analyzer': 'normal_analyzer',
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
                'name': {
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
                'assigned_to': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'stage': {
                    'type': 'integer',
                },
                'stage_name': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'tag': {
                    'type': 'string',
                    'index_analyzer': 'normal_edge_analyzer',
                },
                'amount': {
                    'type': 'float',
                },
                'modified': {
                    'type': 'date',
                },
                'closing_date': {
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
            Account: lambda obj: obj.deal_set.all(),
            Tag: lambda obj: [obj.subject],
        }

    @classmethod
    def prepare_batch(cls, queryset):
        """
        Optimize a queryset for batch indexing.
        """
        return queryset.prefetch_related(
            'account',
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
            'name': obj.name,
            'body': obj.description,
            'account': obj.account_id if obj.account else None,
            'account_name': obj.account.name if obj.account else None,
            'assigned_to': obj.assigned_to.get_full_name() if obj.assigned_to else None,
            'stage': obj.stage,
            'stage_name': Deal.STAGE_CHOICES[obj.stage][1],
            'amount': obj.amount,
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'created': obj.created,
            'closing_date': obj.expected_closing_date,
            'archived': obj.is_archived,
        }

        return prepare_dict(doc)
