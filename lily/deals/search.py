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
            'account': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'customer_id': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer'
                    },
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {
                        'type': 'boolean'
                    },
                }
            },
            'amount_once': {
                'type': 'float',
            },
            'amount_recurring': {
                'type': 'float',
            },
            'assigned_to': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'assigned_to_teams': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'card_sent': {
                'type': 'boolean',
            },
            'closed_date': {
                'type': 'date',
            },
            'contact': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {
                        'type': 'boolean'
                    },
                },
            },
            'contacted_by': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'created': {
                'type': 'date',
            },
            'created_by': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'full_name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'currency': {
                'type': 'string',
            },
            'currency_display': {
                'type': 'string',
            },
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'found_through': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
            'is_archived': {
                'type': 'boolean',
            },
            'is_checked': {
                'type': 'boolean',
            },
            'modified': {
                'type': 'date',
            },
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'new_business': {
                'type': 'boolean',
            },
            'newly_assigned': {
                'type': 'boolean',
            },
            'next_step': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'date_increment': {
                        'type': 'integer'
                    },
                    'position': {
                        'type': 'integer'
                    }
                }
            },
            'next_step_date': {
                'type': 'date',
            },
            'quote_id': {
                'type': 'string'
            },
            'status': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'position': {
                        'type': 'integer'
                    },
                },
            },
            'tags': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                    'object_id': {
                        'type': 'integer'
                    },
                },
            },
            'twitter_checked': {
                'type': 'boolean',
            },
            'why_customer': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
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
            'account': {
                'id': obj.account.id,
                'name': obj.account.name,
                'customer_id': obj.account.customer_id,
                'is_deleted': obj.account.is_deleted,
            } if obj.account else None,
            'amount_once': obj.amount_once,
            'amount_recurring': obj.amount_recurring,
            'assigned_to': {
                'id': obj.assigned_to.id,
                'full_name': obj.assigned_to.full_name,
            } if obj.assigned_to else None,
            'assigned_to_teams': [{
                'id': team.id,
                'name': team.name,
            } for team in obj.assigned_to_teams.all()],
            'card_sent': obj.card_sent,
            'closed_date': obj.closed_date,
            'contact': {
                'id': obj.contact.id,
                'full_name': obj.contact.full_name,
                'is_deleted': obj.contact.is_deleted,
            } if obj.contact else None,
            'contacted_by': {
                'id': obj.contacted_by.id,
                'name': obj.contacted_by.name,
            } if obj.contacted_by else None,
            'content_type': obj.content_type.id,
            'created': obj.created,
            'created_by': {
                'id': obj.created_by.id,
                'full_name': obj.created_by.full_name,
            } if obj.created_by else None,
            'currency': obj.currency,
            'currency_display': obj.get_currency_display(),
            'description': obj.description,
            'found_through': {
                'id': obj.found_through.id,
                'name': obj.found_through.name,
            } if obj.found_through else None,
            'is_archived': obj.is_archived,
            'is_checked': obj.is_checked,
            'modified': obj.modified,
            'name': obj.name,
            'new_business': obj.new_business,
            'next_step': {
                'id': obj.next_step.id,
                'name': obj.next_step.name,
                'date_increment': obj.next_step.date_increment,
                'position': obj.next_step.position,
            } if obj.next_step else None,
            'newly_assigned': obj.newly_assigned,
            'next_step_date': obj.next_step_date,
            'quote_id': obj.quote_id,
            'status': {
                'id': obj.status.id,
                'name': obj.status.name,
                'position': obj.status.position,
            },
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'object_id': tag.object_id,
            } for tag in obj.tags.all()],
            'twitter_checked': obj.twitter_checked,
            'why_customer': {
                'id': obj.why_customer.id,
                'name': obj.why_customer.name,
            } if obj.why_customer else None,
            'why_lost': obj.why_lost.name if obj.why_lost else None,
        }
