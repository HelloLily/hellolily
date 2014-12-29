from elasticutils.contrib.django import Indexable, MappingType

from lily.contacts.models import Function
from lily.search.indexing import prepare_dict
from lily.tags.models import Tag

from .models import Account


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
            'analyzer': 'normal_analyzer',
            '_all': {
                'enabled': False,
            },
            'dynamic_templates': [{
                'phone': {
                    'match': 'phone_*',
                    'mapping': {
                        'type': 'string',
                        'index_analyzer': 'normal_ngram_analyzer'
                    },
                },
            }],
            'properties': {
                'tenant': {
                    'type': 'integer',
                },
                'id': {
                    'type': 'integer'
                },
                'name': {
                    'type': 'string',
                    'index_analyzer': 'normal_ngram_analyzer',
                },
                'contact': {
                    'type': 'integer'
                },
                'email': {
                    'type': 'string',
                    'index_analyzer': 'email_analyzer',
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
            }
        }

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
            Function: lambda obj: [obj.account],
            Tag: lambda obj: [obj.subject],
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
            'functions__contact',
            'assigned_to',
        )

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
            'assigned_to': obj.assigned_to.get_full_name() if obj.assigned_to else None,
            'contact': [contact.id for contact in obj.get_contacts()],
            'tag': [tag.name for tag in obj.tags.all() if tag.name],
            'email': [email.email_address for email in obj.email_addresses.all() if email.email_address],
        }

        phones = obj.phone_numbers.all()
        dedup_phones = set()
        for phone in phones:
            if phone.number not in dedup_phones:
                dedup_phones.add(phone.number)
                if 'phone_' + phone.type not in doc:
                    doc['phone_' + phone.type] = []
                doc['phone_' + phone.type].append(phone.number)

        return prepare_dict(doc)
