from lily.accounts.models import Account

from lily.search.base_mapping import BaseMapping
from lily.tags.models import Tag
from lily.utils.functions import format_phone_number
from lily.utils.models.models import EmailAddress, PhoneNumber, Address
from lily.socialmedia.models import SocialMedia

from .models import Contact, Function


class ContactMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return Contact

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(ContactMapping, cls).get_mapping()
        mapping['properties'].update({
            'accounts': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'customer_id': {
                        'type': 'string'
                    },
                    'function': {
                        'type': 'string'
                    },
                    'phone_numbers': {
                        'type': 'object',
                        'properties': {
                            'number': {
                                'type': 'string',
                                'index_analyzer': 'normal_ngram_analyzer',
                            },
                            'formatted_number': {
                                'type': 'string',
                                'index_analyzer': 'normal_ngram_analyzer',
                            },
                        },
                    }
                }
            },
            'full_name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
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
            'title': {
                'type': 'string',
                'index': 'no',
            },
            'salutation': {
                'type': 'string',
                'index': 'no',
            },
            'gender': {
                'type': 'string',
                'index': 'no',
            },
            'function': {
                'type': 'string',
                'index': 'no',
            },
            'address': {
                'type': 'string',
                'index': 'no',
            },
            'last_name': {
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
            'created': {
                'type': 'date',
            },
            'modified': {
                'type': 'date',
            },
            'active_at': {
                'type': 'integer',
            },
        })
        return mapping

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
            Function: lambda obj: [obj.contact],
            Account: lambda obj: [f.contact for f in obj.functions.all()],
            Tag: lambda obj: [obj.subject],
            EmailAddress: lambda obj: obj.contact_set.all(),
            PhoneNumber: lambda obj: obj.contact_set.all(),
            Address: lambda obj: obj.contact_set.all(),
            SocialMedia: lambda obj: obj.contact_set.all(),
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
            'addresses',
            'functions__account',
        )

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        functions = obj.functions.filter(account__is_deleted=False)

        doc = {
            'addresses': [{
                'address': address.address,
                'postal_code': address.postal_code,
                'city': address.city,
                'state_province': address.state_province,
                'country': address.get_country_display() if address.country else None,
                'type': address.get_type_display(),
            } for address in obj.addresses.all()],
            'content_type':
                obj.content_type.id,
            'created':
                obj.created,
            'description':
                obj.description,
            'email_addresses': [{
                'id': email.id,
                'email_address': email.email_address,
                'status': email.status,
                'is_active': email.is_active,
            } for email in obj.email_addresses.all()],
            'first_name':
                obj.first_name,
            'full_name':
                obj.full_name,
            'gender':
                obj.get_gender_display(),
            'last_name':
                obj.last_name,
            'modified':
                obj.modified,
            'phone_numbers': [{
                'id': phone_number.id,
                'number': phone_number.number,
                'formatted_number': format_phone_number(phone_number.number),
                'type': phone_number.type,
                'status': phone_number.status,
                'status_name': phone_number.get_status_display(),
            } for phone_number in obj.phone_numbers.all()],
            'salutation':
                obj.get_salutation_display(),
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
            'title':
                obj.title,
            'active_at': [f.account_id for f in functions if f.is_active]
        }

        for function in functions:
            account = {
                'id':
                    function.account_id,
                'name':
                    function.account.name if function.account.name else '',
                'customer_id':
                    function.account.customer_id,
                'function':
                    function.title,
                'is_active':
                    function.is_active,
                'phone_numbers': [{
                    'number': phone_number.number,
                    'formatted_number': format_phone_number(phone_number.number),
                } for phone_number in function.account.phone_numbers.all()],
                'domains': [website.full_domain for website in function.account.websites.all()],
            }

            doc.setdefault('accounts', []).append(account)

        return doc
