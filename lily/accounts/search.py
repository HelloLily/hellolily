from lily.accounts.models import Website
from lily.contacts.models import Function
from lily.search.base_mapping import BaseMapping
from lily.socialmedia.models import SocialMedia
from lily.tags.models import Tag
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
        mapping.update({
            'dynamic_templates': [{
                'phone': {
                    'match': 'phone_*',
                    'mapping': {
                        'type': 'string',
                        'index_analyzer': 'normal_ngram_analyzer'
                    },
                },
            }],
        })
        mapping['properties'].update({
            'customer_id': {
                'type': 'string',
            },
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'contact': {
                'type': 'integer'
            },
            'email_addresses': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'email_address': {
                        'type': 'string',
                        'analyzer': 'email_analyzer',
                    },
                    'status': {'type': 'integer'},
                }
            },
            'tag': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'assigned_to': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'created': {
                'type': 'date',
            },
            'modified': {
                'type': 'date',
            },
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'website': {
                'type': 'string',
                'index_analyzer': 'website_analyzer',
            },
            'second_level_domain': {
                'type': 'string',
                'index': 'not_analyzed',
            },
            'address_full': {
                'type': 'string',
                'index': 'no',
            },
            'address': {
                'type': 'object',
                'index': 'no',
                'properties': {
                    'address_street': {'type': 'string'},
                    'address_street_number': {'type': 'integer'},
                    'address_complement': {'type': 'string'},
                    'address_postal_code': {'type': 'string'},
                    'address_city': {'type': 'string'},
                    'address_country': {'type': 'string'},
                },
            },
            'social': {
                'type': 'object',
                'index': 'no',
                'properties': {
                    'social_name': {'type': 'string'},
                    'social_url': {'type': 'string'},
                    'social_profile': {'type': 'string'},
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
            'customer_id': obj.customer_id,
            'name': obj.name,
            'modified': obj.modified,
            'created': obj.created,
            'assigned_to': obj.assigned_to.get_full_name() if obj.assigned_to else None,
            'contact': [contact.id for contact in obj.get_contacts()],
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'email_addresses': [{
                'id': email.id,
                'email_address': email.email_address,
                'status': email.status,
            } for email in obj.email_addresses.all()],
            'description': obj.description,
            'website': [website.website for website in obj.websites.all()],
            'second_level_domain': [website.second_level for website in obj.websites.all()],
            'address': [{
                'address_street': address.street,
                'address_street_number': address.street_number,
                'address_complement': address.complement,
                'address_postal_code': address.postal_code,
                'address_city': address.city,
                'address_country': address.get_country_display()
            } for address in obj.addresses.all()],
            'social': [{
                'social_name': soc.get_name_display(),
                'social_profile': soc.username,
                'social_url': soc.profile_url
            } for soc in obj.social_media.all()],
            'address_full': [address.full() for address in obj.addresses.all()],
        }

        phones = obj.phone_numbers.all()
        dedup_phones = set()
        for phone in phones:
            if phone.number not in dedup_phones:
                dedup_phones.add(phone.number)
                if 'phone_' + phone.type not in doc:
                    doc['phone_' + phone.type] = []
                doc['phone_' + phone.type].append(phone.number)

        return doc
