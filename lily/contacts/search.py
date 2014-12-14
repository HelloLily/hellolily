from elasticutils.contrib.django import Indexable, MappingType

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function
from lily.tags.models import Tag
from lily.utils.models.models import EmailAddress, PhoneNumber


class ContactMapping(MappingType, Indexable):
    @classmethod
    def get_model(cls):
        return Contact

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        return {
            '_all': {
                'enabled': False,
            },
            'dynamic_templates': [{
                'phone': {
                    'match': 'phone_*',
                    'mapping': {
                        'type': 'string',
                        'index': 'analyzed',
                        'search_analyzer': 'letter_analyzer',
                        'index_analyzer': 'letter_ngram_analyzer'
                    },
                },
            }],
            'properties': {
                'tenant': {
                    'type': 'integer',
                },
                'id': {
                    'type': 'integer',
                },
                'name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'search_analyzer': 'letter_analyzer',
                    'index_analyzer': 'letter_ngram_analyzer',
                },
                'last_name': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
                'email': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'letter_analyzer',
                },
                'tag': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'letter_analyzer',
                },
                'account_name': {
                    'type': 'string',
                    'index': 'analyzed',
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
            }
        }

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
        }

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
            'name': obj.full_name(),
            'last_name': obj.last_name,
            'created': obj.created,
            'modified': obj.modified,
        }

        functions = obj.functions.all()
        if functions:
            doc['account'] = [function.account_id for function in functions]
            doc['account_name'] = [function.account.name for function in functions if function.account.name]

        phones = obj.phone_numbers.all().distinct('number')
        for phone in phones:
            if 'phone_' + phone.type not in doc:
                doc['phone_' + phone.type] = []
            doc['phone_' + phone.type].append(phone.number)

        emails = obj.email_addresses.all()
        emails = list(set([email.email_address for email in emails if email.email_address]))
        if emails:
            doc['email'] = emails

        tags = obj.tags.all()
        tags = [tag.name for tag in tags if tag.name]
        if tags:
            doc['tag'] = tags

        return doc
