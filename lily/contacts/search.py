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
            'email': {
                'type': 'string',
                'index_analyzer': 'email_analyzer',
            },
            'tag': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'account_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'account': {
                'type': 'integer',
            },
            'created': {
                'type': 'date',
            },
            'modified': {
                'type': 'date',
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
        doc = {
            'name': obj.full_name(),
            'last_name': obj.last_name,
            'created': obj.created,
            'modified': obj.modified,
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'email': [email.email_address for email in obj.email_addresses.all() if email.email_address],
            'description': obj.description,
            'social': [{'social_name': soc.get_name_display(),
                        'social_profile': soc.username,
                        'social_url': soc.profile_url} for soc in obj.social_media.all()],
            'title': obj.title,
            'salutation': obj.get_salutation_display(),
            'gender': obj.get_gender_display(),
            'address': [address.full() for address in obj.addresses.all()],
        }

        functions = obj.functions.all()
        if functions:
            doc['account'] = [function.account_id for function in functions]
            doc['account_name'] = [function.account.name for function in functions if function.account.name]
            doc['function'] = sorted(functions, key=lambda o: o.created, reverse=True)[0].title

        phones = obj.phone_numbers.all()
        dedup_phones = set()
        for phone in phones:
            if phone.number not in dedup_phones:
                dedup_phones.add(phone.number)
                if 'phone_' + phone.type not in doc:
                    doc['phone_' + phone.type] = []
                doc['phone_' + phone.type].append(phone.number)

        return doc
