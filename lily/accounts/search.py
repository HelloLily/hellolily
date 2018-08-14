from lily.accounts.models import Website
from lily.contacts.models import Function
from lily.search.base_mapping import BaseMapping
from lily.socialmedia.models import SocialMedia
from lily.tags.models import Tag
from lily.utils.functions import format_phone_number
from lily.utils.models.models import EmailAddress, PhoneNumber, Address

from .models import Account


class AccountMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return Account

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(AccountMapping, cls).get_mapping()
        mapping['properties'].update({
            'address_full': {
                'type': 'string',
                'index': 'no',
            },
            'addresses': {
                'type': 'object',
                'index': 'no',
                'properties': {
                    'address': {
                        'type': 'string'
                    },
                    'postal_code': {
                        'type': 'string'
                    },
                    'city': {
                        'type': 'string'
                    },
                    'country': {
                        'type': 'string'
                    },
                },
            },
            'assigned_to': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'customer_id': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'created': {
                'type': 'date',
            },
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'email_addresses': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'email_address': {
                        'type': 'string',
                        'analyzer': 'email_analyzer',
                    },
                    'status': {
                        'type': 'integer'
                    },
                }
            },
            'modified': {
                'type': 'date',
            },
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'name_words': {
                'type': 'string',
                'index_analyzer': 'simple',
            },
            'phone_numbers': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'number': {
                        'type': 'string',
                        'index_analyzer': 'normal_ngram_analyzer',
                    },
                    'formatted_number': {
                        'type': 'string',
                        'index_analyzer': 'normal_ngram_analyzer',
                    },
                    'type': {
                        'type': 'string'
                    },
                    'status': {
                        'type': 'integer'
                    },
                    'status_name': {
                        'type': 'string'
                    },
                }
            },
            'status': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer'
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
            'websites': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'website': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                    'is_primary': {
                        'type': 'boolean'
                    },
                }
            },
            'social_media': {
                'type': 'object',
                'index': 'no',
                'properties': {
                    'name': {
                        'type': 'string'
                    },
                    'profile_url': {
                        'type': 'string'
                    },
                    'username': {
                        'type': 'string'
                    },
                },
            },
            'domain': {
                'type': 'string',
                'index_analyzer': 'domain_analyzer',
            },
            'second_level_domain': {
                'type': 'string',
                'index': 'not_analyzed',
            },
        })
        return mapping

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
            Function: lambda obj: [obj.account],
            Tag: lambda obj: [obj.subject],
            Website: lambda obj: [obj.account],
            EmailAddress: lambda obj: obj.account_set.all(),
            PhoneNumber: lambda obj: obj.account_set.all(),
            Address: lambda obj: obj.account_set.all(),
            SocialMedia: lambda obj: obj.account_set.all(),
            # LilyUser saves every login, which will trigger reindex of all related accounts.
            # LilyUser: lambda obj: obj.account_set.all(),
        }

    @classmethod
    def prepare_batch(cls, queryset):
        """
        Optimize a queryset for batch indexing.
        """
        return queryset.prefetch_related(
            'tags',
            'email_addresses',
            'phone_numbers',
            'social_media',
            'websites',
            'addresses',
            'functions__contact',
            'assigned_to',
        )

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        doc = {
            'address_full': [address.full() for address in obj.addresses.all()],
            'addresses': [{
                'address': address.address,
                'postal_code': address.postal_code,
                'city': address.city,
                'country': address.get_country_display() if address.country else None,
            } for address in obj.addresses.all()],
            'assigned_to':
                obj.assigned_to.full_name if obj.assigned_to else None,
            'content_type':
                obj.content_type.id,
            'created':
                obj.created,
            'customer_id':
                obj.customer_id,
            'description':
                obj.description,
            'email_addresses': [{
                'id': email.id,
                'email_address': email.email_address,
                'status': email.status,
                'is_active': email.is_active,
            } for email in obj.email_addresses.all()],
            'modified':
                obj.modified,
            'name':
                obj.name,
            'name_words':
                obj.name,
            'phone_numbers': [{
                'id': phone_number.id,
                'number': phone_number.number,
                'formatted_number': format_phone_number(phone_number.number),
                'type': phone_number.type,
                'status': phone_number.status,
                'status_name': phone_number.get_status_display(),
            } for phone_number in obj.phone_numbers.all()],
            'status': {
                'id': obj.status.id,
                'name': obj.status.name,
            } if obj.status else None,
            'social_media': [{
                'id': soc.id,
                'name': soc.get_name_display(),
                'username': soc.username,
                'profile_url': soc.profile_url
            } for soc in obj.social_media.all()],
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'object_id': tag.object_id,
            } for tag in obj.tags.all()],
            'websites': [{
                'id': website.id,
                'website': website.website,
                'is_primary': website.is_primary,
            } for website in obj.websites.all()],

            # Fields not returned by the serializer.
            'domain': [website.full_domain for website in obj.websites.all()],
            'second_level_domain': [website.second_level for website in obj.websites.all()],
        }

        return doc
