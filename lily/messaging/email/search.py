from bs4 import BeautifulSoup
from lily.search.base_mapping import BaseMapping

from .models.models import EmailMessage
from python_imap.utils import convert_br_to_newline


class EmailMessageMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return EmailMessage

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """

        mapping = super(EmailMessageMapping, cls).get_mapping()
        mapping['properties'].update({
            'account': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {
                        'type': 'string',
                        'index_analyzer': 'normal_edge_analyzer',
                    },
                    'email': {
                        'type': 'string',
                        'analyzer': 'email_analyzer',
                    },
                    'privacy': {'type': 'integer'},
                }
            },
            'label_id': {
                'type': 'string',
                'index_analyzer': 'normal_analyzer',
            },
            'sender_email': {
                'type': 'string',
                'analyzer': 'email_analyzer',
            },
            'sender_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'received_by_email': {
                'type': 'string',
                'analyzer': 'email_analyzer',
            },
            'received_by_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'received_by_cc_email': {
                'type': 'string',
                'analyzer': 'email_analyzer',
            },
            'received_by_cc_name': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'subject': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'sent_date': {
                'type': 'date',
            },
            'read': {
                'type': 'boolean',
            },
            'snippet': {
                'type': 'string',
                'index_analyzer': 'normal_edge_analyzer',
            },
            'has_attachment': {
                'type': 'boolean',
            },
            'message_id': {
                'type': 'string',
                'index_analyzer': 'keyword',
            },
            'thread_id': {
                'type': 'string',
                'index_analyzer': 'keyword',
            },
            'body': {
                'type': 'string',
                'index_analyzer': 'normal_analyzer',
            },
            'is_trashed': {
                'type': 'boolean',
            },
            'is_starred': {
                'type': 'boolean',
            },
            'is_spam': {
                'type': 'boolean',
            },
            'is_draft': {
                'type': 'boolean',
            },
            'is_archived': {
                'type': 'boolean',
            },
        })
        return mapping

    @classmethod
    def get_related_models(cls):
        """
        Maps related models, how to get an instance list from a signal sender.
        """
        return {
            # Account: lambda obj: obj.deal_set.all(),
            # Tag: lambda obj: [obj.subject],
        }

    @classmethod
    def prepare_batch(cls, queryset):
        """
        Optimize a queryset for batch indexing.
        """
        return queryset.prefetch_related(
            'received_by',
            'received_by_cc',
            'labels',
            'account',
        ).select_related(
            'sender',
        )

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'account': {
                'id': obj.account.id,
                'name': obj.account.label,
                'email': obj.account.email_address,
                'privacy': obj.account.privacy,
            },
            'subject': obj.subject,
            'sent_date': obj.sent_date,
            'read': obj.read,
            'snippet': obj.snippet,
            'has_attachment': obj.has_attachment,
            'label_id': [label.label_id for label in obj.labels.all() if label.label_id],
            'label_name': [label.name for label in obj.labels.all() if label.name],
            'sender_email': obj.sender.email_address,
            'sender_name': obj.sender.name,
            'received_by_email':
                [receiver.email_address for receiver in obj.received_by.all() if receiver.email_address],
            'received_by_name': [receiver.name for receiver in obj.received_by.all() if receiver.name],
            'received_by_cc_email':
                [receiver.email_address for receiver in obj.received_by_cc.all() if receiver.email_address],
            'received_by_cc_name': [receiver.name for receiver in obj.received_by_cc.all() if receiver.name],
            'message_id': obj.message_id,
            'thread_id': obj.thread_id,
            'body': obj.body_text or cls.body_html_parsed(obj),
            'is_trashed': obj.is_trashed,
            'is_starred': obj.is_starred,
            'is_spam': obj.is_spam,
            'is_draft': obj.is_draft,
            'is_archived': obj.is_archived,
        }

    @classmethod
    def has_deleted(cls):
        return False

    @classmethod
    def body_html_parsed(cls, obj):
        soup = BeautifulSoup(obj.body_html, 'lxml', from_encoding='utf-8')
        soup = convert_br_to_newline(soup)
        return soup.get_text()
