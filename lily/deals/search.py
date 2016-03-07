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
            'account_customer_id': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
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
            'assigned_to_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'assigned_to_id': {
                'type': 'integer',
            },
            'created_by_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'created_by_id': {
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
            'closed_date': {
                'type': 'date',
            },
            'is_checked': {
                'type': 'boolean',
            },
            'archived': {
                'type': 'boolean',
            },
            'feedback_form_sent': {
                'type': 'boolean',
            },
            'twitter_checked': {
                'type': 'boolean',
            },
            'card_sent': {
                'type': 'boolean',
            },
            'found_through': {
                'type': 'integer',
            },
            'found_through_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'contacted_by': {
                'type': 'integer',
            },
            'contacted_by_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'quote_id': {
                'type': 'string'
            },
            'next_step': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'date_increment': {'type': 'integer'},
                    'position': {'type': 'integer'}
                }
            },
            'next_step_date': {
                'type': 'date',
            },
            'why_customer': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'why_lost': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
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
            'account_customer_id': obj.account.customer_id if obj.account else None,
            'account_name': obj.account.name if obj.account else None,
            'contact': obj.contact_id if obj.contact else None,
            'contact_name': obj.contact.full_name() if obj.contact else None,
            'assigned_to_name': obj.assigned_to.get_full_name() if obj.assigned_to else None,
            'assigned_to_id': obj.assigned_to.id if obj.assigned_to else None,
            'created_by': obj.created_by.get_full_name() if obj.created_by else None,
            'stage': obj.stage,
            'stage_name': obj.get_stage_display(),
            'amount_once': obj.amount_once,
            'amount_recurring': obj.amount_recurring,
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'created': obj.created,
            'modified': obj.modified,
            'closed_date': obj.closed_date,
            'is_checked': obj.is_checked,
            'archived': obj.is_archived,
            'feedback_form_sent': obj.feedback_form_sent,
            'twitter_checked': obj.twitter_checked,
            'card_sent': obj.card_sent,
            'found_through': obj.found_through,
            'found_through_name': obj.get_found_through_display(),
            'contacted_by': obj.contacted_by,
            'contacted_by_name': obj.get_contacted_by_display(),
            'new_business': obj.new_business,
            'quote_id': obj.quote_id,
            'next_step': {
                'id': obj.next_step.id,
                'name': obj.next_step.name,
                'date_increment': obj.next_step.date_increment,
                'position': obj.next_step.position,
            } if obj.next_step else None,
            'next_step_date': obj.next_step_date,
            'why_customer': obj.why_customer.name if obj.why_customer else None,
            'why_lost': obj.why_lost.name if obj.why_lost else None,
        }
