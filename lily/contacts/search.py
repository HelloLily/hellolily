from elasticutils.contrib.django import Indexable, MappingType

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
            'dynamic_templates': [{
                'phone': {
                    'match': 'phone_*',
                    'mapping': {
                        'type': 'string',
                        'index': 'analyzed',
                        'search_analyzer': 'name_search_analyzer',
                        'index_analyzer': 'name_index_analyzer'
                    },
                },
            }],
            'properties': {
                'id': {
                    'type': 'integer',
                },
                'name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'search_analyzer': 'name_search_analyzer',
                    'index_analyzer': 'name_index_analyzer',
                },
                'email': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'email_analyzer',
                },
                'tag': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'simple',
                },
                'account_name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'simple'
                },
                'account': {
                    'type': 'integer',
                },
                'tenant': {
                    'type': 'integer',
                },
                'created': {
                    'type': 'date',
                    'index': 'no',
                },
                'modified': {
                    'type': 'date',
                },
            }
        }

    @classmethod
    def get_related_models(cls):
        return (Function, EmailAddress, PhoneNumber, Tag)

    @classmethod
    def get_type_set(cls):
        return 'contact_set'

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """
        Converts this instance into an Elasticsearch document.
        """
        if obj is None:
            obj = cls.get_model().objects.get(pk=obj_id)

        doc = {
            'id': obj.id,
            'name': '%s %s' % (obj.first_name, obj.last_name),
            'tenant': obj.tenant_id,
            'created': obj.created,
            'modified': obj.modified,
        }

        functions = obj.functions.all()
        if functions:
            doc['account'] = [function.account_id for function in functions]
            doc['account_name'] = [function.account.name for function in functions if function.account.name]

        phones = obj.phone_numbers.all()
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
