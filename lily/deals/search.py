from lily.accounts.models import Account
from lily.search.base_mapping import BaseMapping
from lily.tags.models import Tag

from .models import Deal


class DealMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return Deal

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(DealMapping, cls).get_mapping()
        mapping['properties'].update({
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
            'assigned_to_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'assigned_to_id': {
                'type': 'integer',
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
            'amount_once': {
                'type': 'float',
            },
            'amount_recurring': {
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
            'feedback_form_sent': {
                'type': 'boolean',
            }
        })
        return mapping

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
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'name': obj.name,
            'body': obj.description,
            'account': obj.account_id if obj.account else None,
            'account_name': obj.account.name if obj.account else None,
            'assigned_to_name': obj.assigned_to.get_full_name() if obj.assigned_to else None,
            'assigned_to_id': obj.assigned_to.id,
            'stage': obj.stage,
            'stage_name': obj.get_stage_display(),
            'amount_once': obj.amount_once,
            'amount_recurring': obj.amount_recurring,
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'created': obj.created,
            'modified': obj.modified,
            'closing_date': obj.expected_closing_date,
            'archived': obj.is_archived,
            'feedback_form_sent': obj.feedback_form_sent,
            'new_business': obj.new_business
        }
