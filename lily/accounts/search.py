from elasticutils.contrib.django import Indexable, MappingType

from lily.accounts.models import Account
from lily.contacts.models import Function


class AccountMapping(MappingType, Indexable):
    @classmethod
    def get_model(cls):
        return Account

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        return {
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
                'id': {'type': 'integer'},
                'name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'search_analyzer': 'letter_analyzer',
                    'index_analyzer': 'letter_ngram_analyzer',
                },
                'contact': {
                    'type': 'integer'
                },
                'email': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'email_analyzer',
                },
                'tag': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'letter_analyzer',
                },
                'assigned_to': {
                    'type': 'string',
                    'index': 'analyzed',
                    'search_analyzer': 'letter_analyzer',
                    'index_analyzer': 'letter_ngram_analyzer',
                },
                'tenant': {
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
            Function: lambda obj: [obj.account],
            # LilyUser saves every login, which will trigger reindex of all related accounts.
            # LilyUser: lambda obj: obj.account_set.all(),
        }

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """
        Converts this instance into an Elasticsearch document.
        """
        if obj is None:
            obj = cls.get_model().objects.get(pk=obj_id)

        doc = {
            'id': obj.id,
            'name': obj.name,
            'tenant': obj.tenant_id,
            'modified': obj.modified,
            'created': obj.created,
        }

        if obj.assigned_to:
            doc['assigned_to'] = obj.assigned_to.get_full_name()

        contacts = [contact.id for contact in obj.get_contacts()]
        doc['contact'] = contacts

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
