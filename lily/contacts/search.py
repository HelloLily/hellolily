from lily.accounts.models import Account

from lily.search.base_mapping import BaseMapping
from lily.tags.models import Tag
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
        mapping.update({
            'dynamic_templates': [{
                'phone': {
                    'match': 'phone_*',
                    'mapping': {
                        'type': 'string',
                        'index': 'analyzed',
                        'index_analyzer': 'normal_ngram_analyzer'
                    },
                },
            }],
        })
        mapping['properties'].update({
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'description': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
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
            'created': {
                'type': 'date',
            },
            'modified': {
                'type': 'date',
            },
            'accounts': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                    'customer_id': {'type': 'string'},
                    'function': {'type': 'string'}
                }
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
            EmailAddress: lambda obj: obj.contacts.all(),
            PhoneNumber: lambda obj: obj.contacts.all(),
            Address: lambda obj: obj.contacts.all(),
            SocialMedia: lambda obj: obj.contacts.all(),
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
        doc = {
            'name': obj.full_name(),
            'last_name': obj.last_name,
            'created': obj.created,
            'modified': obj.modified,
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'email_addresses': [{
                'id': email.id,
                'email_address': email.email_address,
                'status': email.status,
            } for email in obj.email_addresses.all()],
            'description': obj.description,
            'social': [{'social_name': soc.get_name_display(),
                        'social_profile': soc.username,
                        'social_url': soc.profile_url} for soc in obj.social_media.all()],
            'title': obj.title,
            'salutation': obj.get_salutation_display(),
            'gender': obj.get_gender_display(),
            'address': [address.full() for address in obj.addresses.all()],
            'addresses': [{
                'street': address.street,
                'street_number': address.street_number,
                'complement': address.complement,
                'postal_code': address.postal_code,
                'city': address.city,
                'state_province': address.state_province,
                'country': address.get_country_display(),
                'type': address.get_type_display(),
            } for address in obj.addresses.all()],
        }

        functions = obj.functions.all()

        for function in functions:
            account = {
                'id': function.account_id,
                'name': function.account.name if function.account.name else '',
                'customer_id': function.account.customer_id,
                'function': function.title
            }

            doc.setdefault('accounts', []).append(account)

        phones = obj.phone_numbers.all()
        dedup_phones = set()
        for phone in phones:
            if phone.number not in dedup_phones:
                dedup_phones.add(phone.number)
                if 'phone_' + phone.type not in doc:
                    doc['phone_' + phone.type] = []
                doc['phone_' + phone.type].append(phone.number)

        return doc
