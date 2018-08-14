from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.search.base_mapping import BaseMapping
from lily.tags.models import Tag

from .models import Case


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
        mapping['properties'].update({
            'account': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {
                        'type': 'boolean'
                    },
                },
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
            'contact': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'is_deleted': {
                        'type': 'boolean'
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
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'expires': {
                'type': 'date',
            },
            'is_archived': {
                'type': 'boolean',
            },
            'modified': {
                'type': 'date',
            },
            'newly_assigned': {
                'type': 'boolean',
            },
            'priority': {
                'type': 'integer',
            },
            'priority_display': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
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
                },
            },
            'subject': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
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
            'type': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                },
            },
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
            'account': {
                'id': obj.account.id,
                'name': obj.account.name,
                'is_deleted': obj.account.is_deleted,
            } if obj.account else None,
            'assigned_to': {
                'id': obj.assigned_to.id,
                'full_name': obj.assigned_to.full_name,
            } if obj.assigned_to else None,
            'assigned_to_teams': [{
                'id': team.id,
                'name': team.name,
            } for team in obj.assigned_to_teams.all()],
            'contact': {
                'id': obj.contact.id,
                'full_name': obj.contact.full_name,
                'is_deleted': obj.contact.is_deleted,
            } if obj.contact else None,
            'content_type': obj.content_type.id,
            'created': obj.created,
            'created_by': {
                'id': obj.created_by.id,
                'full_name': obj.created_by.full_name,
            } if obj.created_by else None,
            'description': obj.description,
            'expires': obj.expires,
            'is_archived': obj.is_archived,
            'modified': obj.modified,
            'newly_assigned': obj.newly_assigned,
            'priority': obj.priority,
            'priority_display': obj.get_priority_display(),
            'status': {
                'id': obj.status.id,
                'name': obj.status.name,
            },
            'subject': obj.subject,
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'object_id': tag.object_id,
            } for tag in obj.tags.all()],
            'type': {
                'id': obj.type.id,
                'name': obj.type.name,
            } if obj.type else None,
            'parcel_provider': obj.parcel.get_provider_display() if obj.parcel else None,
            'parcel_identifier': obj.parcel.identifier if obj.parcel else None,
            'parcel_link': obj.parcel.get_link() if obj.parcel else None,
        }
