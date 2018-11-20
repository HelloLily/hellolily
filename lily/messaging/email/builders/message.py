import datetime
import email
import gc
import logging
import re

from dateutil.parser import parse
from django.conf import settings
from django.db import transaction
import pytz

from lily.messaging.email.connector import LabelNotFoundError
from lily.messaging.email.utils import determine_message_type

from ..models.models import EmailMessage, EmailHeader, Recipient, NoEmailMessageId
from .utils import get_attachments_from_payload, get_body_html_from_payload, get_body_text_from_payload

logger = logging.getLogger(__name__)


class MessageBuilderException(Exception):
    pass


class AttachmentException(MessageBuilderException):
    pass


class MessageBuilder(object):
    """
    Builder to get, create or update Messages
    """
    def __init__(self, manager):
        self.manager = manager
        self.message = None
        self.labels = []
        self.headers = []
        self.received_by = None
        self.received_by_cc = None
        self.attachments = []
        self.created = False

    def get_or_create_message(self, message_dict):
        """
        Get or create EmailMessage.

        Arguments:
            message_dict (dict): with label information

        Returns:
            message (instance): unsaved message
            created (boolean): True if label is created
        """
        # Reset current builder info.
        self.message = None
        self.labels = []
        self.headers = []
        self.received_by = set()
        self.received_by_cc = set()
        self.attachments = []

        # Prevent memory leaks.
        gc.collect()

        # Get or create without save.
        created = False
        try:
            self.message = EmailMessage.objects.get(
                message_id=message_dict['id'],
                account=self.manager.email_account,
            )
        except EmailMessage.DoesNotExist:
            self.message = EmailMessage(
                message_id=message_dict['id'],
                account=self.manager.email_account,
            )
            created = True

        if 'threadId' in message_dict:
            self.message.thread_id = message_dict['threadId']

        return self.message, created

    def store_message_info(self, message_info, message_id):
        """
        With given dict, create or update current message.

        Args:
            message_info (dict): with message info
            message_id (string): message_id of email
        """
        self.store_labels_and_thread_for_message(message_info, message_id)
        self.message.snippet = message_info['snippet']
        self._save_message_payload(message_info['payload'])
        self._save_message_type()

    def store_labels_and_thread_for_message(self, message_info, message_id):
        """
        Handle the labels and thread_id for current EmailMessage

        Args:
            message_info (dict): message info dict
            message_id (string): message_id of email
        """
        _, self.created = self.get_or_create_message({'id': message_id})
        self.message.thread_id = message_info['threadId']

        # Set boolean identifier for some labels for faster filtering.
        labels = message_info.get('labelIds', [])
        self.message.read = settings.GMAIL_LABEL_UNREAD not in labels
        self.message.is_inbox_message = settings.GMAIL_LABEL_INBOX in labels
        self.message.is_sent_message = settings.GMAIL_LABEL_SENT in labels
        self.message.is_draft_message = settings.GMAIL_LABEL_DRAFT in labels
        self.message.is_trashed_message = settings.GMAIL_LABEL_TRASH in labels
        self.message.is_spam_message = settings.GMAIL_LABEL_SPAM in labels
        self.message.is_starred_message = settings.GMAIL_LABEL_STAR in labels

        # Get the available Label objects for the message from the database and the missing ones by the API.
        # First, get all labels from the database.
        db_labels = self.manager.email_account.labels.all()

        message_label_set = set(label for label in labels)
        # Remove labels the we won't use in Lily.
        remove = {'CATEGORY_PROMOTIONS', 'IMPORTANT', 'CATEGORY_FORUMS', 'CHAT', 'CATEGORY_SOCIAL', 'CATEGORY_UPDATES',
                  'CATEGORY_PERSONAL'}
        message_label_set = message_label_set - remove
        db_label_set = set(label.label_id for label in db_labels)

        # Use set operations to get the available and missing labels.
        # Labels that exist in Gmail for this message but are not in our db.
        missing_label_ids = message_label_set - db_label_set
        if missing_label_ids:
            # Labels missing in our database should be retrieved by the API.
            for label_id in missing_label_ids:
                try:
                    db_label = self.manager.get_label(label_id, use_db=False)
                    self.labels.append(db_label)
                except LabelNotFoundError:
                    logger.error(
                        'Label {} missing in db also not found via API for {}'.format(
                            label_id,
                            self.manager.email_account
                        )
                    )

        # Labels that exist both in Gmail and in our db. Those labels are already retrieved from the db above.
        available_label_ids = message_label_set & db_label_set
        if available_label_ids:
            # Use dict comprehension to get a dictionary with the label_id as the keys and the label as the value.
            db_label_dict = {label.label_id: label for label in db_labels}
            for label_id in available_label_ids:
                self.labels.append(db_label_dict[label_id])

    def _save_message_payload(self, payload):
        """
        Walk through message and save headers and parts

        Args:
            payload: dict with message payload
        """
        if 'headers' in payload:
            self._create_message_headers(payload['headers'])

        self.message.body_html = get_body_html_from_payload(payload, self.message.message_id)
        self.message.body_text = get_body_text_from_payload(payload, self.message.message_id)

        self.attachments = get_attachments_from_payload(
            payload,
            self.message.body_html,
            self.message.message_id,
            self.attachments,
            self.manager.connector,
        )

    def _create_message_headers(self, headers):
        """
        Given header dict, create EmailHeaders for message.

        Args:
            headers (dict): of name, value headers
        """
        for header in headers:
            header_name = header['name'].lower()
            header_value = header['value']
            if header_name == 'date':
                date = email.utils.parsedate_tz(header_value)
                if date:
                    self.message.sent_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date), pytz.UTC)
                else:
                    try:
                        date = parse(header_value)
                    except ValueError:
                        pass
                    else:
                        if date:
                            self.message.sent_date = date
            elif header_name == 'subject':
                self.message.subject = header_value
            elif header_name in ['to', 'from', 'cc', 'delivered-to']:
                self._create_recipients(header_name, header_value)
            else:
                if header_name.startswith('message-id') or header_name.startswith('reply-to'):
                    self.headers.append(EmailHeader(
                        name=header['name'],
                        value=header['value'],
                    ))

    def _create_recipients(self, header_name, header_value):
        """
        Create recipient based on header

        Args:
            header_name (string): with name of header
            header_value (string): with value of header
        """
        header_name = header_name.lower()

        # Selects all comma's with the following conditions:
        # 1. Preceded by a TLD (with a max of 16 chars) or
        # 2. Preceded by an angle bracket (>)
        # Then swap out with regex group 1 + a semicolon (\1;)
        # After that split by semicolon (;)
        # Note: Basic tests have shown that char limit on the TLD can be increased without problems
        # 16 chars seems to be enough for now though
        recipients = re.sub(r'(\.[A-Z]{2,16}|>)(,)', r'\1;', header_value, flags=re.IGNORECASE).split('; ')

        for recipient in recipients:
            # Get or create recipient
            email_address = email.utils.parseaddr(recipient)

            if email_address[1] != '':
                recipient = Recipient.objects.get_or_create(
                    name=email_address[0],
                    email_address=email_address[1],
                )[0]

                # Set recipient to correct field
                if header_name == 'from':
                    self.message.sender = recipient
                elif header_name in ['to', 'delivered-to']:
                    self.received_by.add(recipient)
                elif header_name == 'cc':
                    self.received_by_cc.add(recipient)

    def _save_message_type(self):
        if self.created:
            # Only determine message_type at creation, no need to update the message type at label changes.
            if self.message.sent_date and self.message.sender_id:
                # Message is an email, not a chat.
                message_type, message_type_to_id = determine_message_type(
                    self.message.thread_id,
                    self.message.sent_date,
                    self.message.account.email_address
                )
                self.message.message_type = message_type
                if message_type_to_id:
                    self.message.message_type_to_id = message_type_to_id

    def save(self):
        # Only save if there is a sent date, otherwise it's a chat message.
        if self.message.sent_date and self.message.sender_id:

            self.message.skip_signal = True  # Disable intermediate reindexing of the message.

            # Check for attachments.
            if self.attachments:
                self.message.has_attachment = True

            if not self.message.pk:
                # Save before we can add many-to-many and foreign keys.
                self.message.save()

            # Save recipients.
            self.message.received_by.add(*self.received_by)
            self.message.received_by_cc.add(*self.received_by_cc)

            # Save labels.
            if len(self.labels):
                with transaction.atomic():
                    if self.message.pk:
                        self.message.labels.clear()
                    self.message.labels.add(*self.labels)
            elif self.message.labels:
                self.message.labels.clear()

            # Save headers.
            if len(self.headers):
                self.message.headers.all().delete()
                self.message.headers.add(bulk=False, *self.headers)

            # Save attachments.
            if len(self.attachments):
                self.message.attachments.all().delete()
                self.message.attachments.add(bulk=False, *self.attachments)

            self.message.skip_signal = False  # Re-enable indexing of the email on the last save.
            self.message.save()
        else:
            logger.warning('Downloaded a message other than an email.')

            NoEmailMessageId.objects.get_or_create(
                message_id=self.message.message_id,
                account=self.manager.email_account
            )

    def cleanup(self):
        """
        Cleanup references, to prevent reference cycle
        """
        self.manager = None
        self.message = None
        self.labels = []
        self.headers = []
        self.received_by = None
        self.received_by_cc = None
        self.attachments = []
        self.created = False
