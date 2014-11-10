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
                    'index': 'not_analyzed',
                },
                'phone': {
                    'type': 'string',
                    'index': 'analyzed',
                    'search_analyzer': 'name_search_analyzer',
                    'index_analyzer': 'name_index_analyzer',
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
            'modified': obj.modified,
        }

        function = obj.get_primary_function()
        if function:
            doc['account'] = function.account_id

        phone = obj.get_phone_number()
        if phone:
            doc['phone'] = [phone.number]

        email = obj.primary_email()
        if email:
            doc['email'] = [email.email_address]

        tags = obj.tags.all()
        tag_names = filter(None, [tag.name for tag in tags])
        if tag_names:
            doc['tag'] = tag_names

        return doc
