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
            'properties': {
                'id': {'type': 'integer'},
                'name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'search_analyzer': 'letter_analyzer',
                    'index_analyzer': 'letter_ngram_analyzer',
                },
                'contact': {'type': 'integer'},
                'assigned_to': {'type': 'string'},
                'tenant': {'type': 'integer'},
                'modified': {'type': 'date'},
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
        }

        if obj.assigned_to:
            doc.update({
                'assigned_to': obj.assigned_to.get_full_name(),
            })

        contacts = [contact.id for contact in obj.get_contacts()]
        doc['contact'] = contacts
        return doc
