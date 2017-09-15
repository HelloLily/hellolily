import base64
import datetime
import email
import gc
import logging
import re
import StringIO

from bs4 import BeautifulSoup, UnicodeDammit
from dateutil.parser import parse
from django.conf import settings
from django.core.files import File
from django.db import transaction
import pytz

from lily.messaging.email.utils import get_extensions_for_type

from ..models.models import EmailMessage, EmailHeader, Recipient, EmailAttachment, NoEmailMessageId

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
        self.inline_attachments = {}

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
        self.inline_attachments = {}

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
        # Save labels
        self.store_labels_and_thread_for_message(message_info, message_id)

        self.message.snippet = message_info['snippet']

        # Save the payload
        self._save_message_payload(message_info['payload'])

    def store_labels_and_thread_for_message(self, message_info, message_id):
        """
        Handle the labels and thread_id for current EmailMessage

        Args:
            message_info (dict): message info dict
            message_id (string): message_id of email
        """
        self.get_or_create_message({'id': message_id})
        self.message.thread_id = message_info['threadId']

        # UNREAD identifier check to see if message is read.
        self.message.read = settings.GMAIL_LABEL_UNREAD not in message_info.get('labelIds', [])

        # Get the available Label objects for the message from the database and the missing ones by the API.
        # First, get all labels from the database.
        db_labels = self.manager.email_account.labels.all()

        message_label_set = set(label for label in message_info.get('labelIds', []))
        db_label_set = set(label.label_id for label in db_labels)

        # Use set operations to get the available and missing labels.
        # Labels that exist in Gmail for this message but are not in our db.
        missing_label_ids = message_label_set - db_label_set
        if missing_label_ids:
            # Labels missing in our database should be retrieved by the API.
            for label_id in missing_label_ids:
                db_label = self.manager.get_label(label_id, use_db=False)
                self.labels.append(db_label)

        # Labels that exist both in Gmail and in our db. Those labels are already retrieved from the db above.
        available_label_ids = message_label_set & db_label_set
        if available_label_ids:
            # Use dict comprehension to get a dictonary with the label_id as the keys and the label as the value.
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

        self.message.body_html = ''
        self.message.body_text = ''

        # Check Message is split up in parts
        if 'parts' in payload:
            for part in payload['parts']:
                self._parse_message_part(part)
        else:
            self._parse_message_part(payload)

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

    def _parse_message_part(self, part):
        """
        Parse message part

        Args:
            part: dict with message part
        """
        # Check if part has child parts.
        if 'parts' in part:
            for part in part['parts']:
                self._parse_message_part(part)
        else:
            part_headers = self._headers_to_dict(part.get('headers', {}))

            # Get content type.
            mime_type = part['mimeType']

            # Check if part is an attachment.
            if part['filename'] or 'data' not in part['body'] or mime_type == 'text/css':
                self._create_attachment(part, part_headers)

            # Handle non attachment.
            else:
                # Decode body part.
                body = base64.urlsafe_b64decode(part['body']['data'].encode())

                encoding = None
                if part_headers:
                    encoding = self._get_encoding_from_headers(part_headers)

                if mime_type == 'text/html':
                    self._create_body_html(body, encoding)

                elif mime_type == 'text/plain':
                    self._create_body_text(body, encoding)

                elif mime_type == 'text/xml':
                    # Conversation xml, do not store.
                    pass
                elif mime_type == 'text/rfc822-headers':
                    # Header part, not needed.
                    pass
                elif mime_type in (
                        'text/css',
                        'application/octet-stream',
                        'image/gif',
                        'image/jpg',
                        'image/x-png',
                        'image/png',
                        'image/jpeg',
                ):
                    # Attachments.
                    self._create_attachment(part, part_headers)
                else:
                    self._create_attachment(part, part_headers)
                    logging.warning('other mime_type %s for message %s, account %s' % (
                        mime_type,
                        self.message.message_id,
                        self.manager.email_account,
                    ))

    def _create_attachment(self, part, headers):
        """
        Create an attachment for the given part.

        Args:
            part (dict): with attachment info
            headers (dict): headers for message part

        Raises:
            Attachment exception if attachment couldn't be created.
        """
        logger.debug('Storing attachment for message %s' % self.message.message_id)
        headers = {name.lower(): value for name, value in headers.iteritems()}

        # Check if attachment is inline.
        inline = False
        if headers and headers.get('content-id', False):
            inline = True

        # Get file data from part or from remote.
        if 'data' in part['body']:
            file_data = part['body']['data']
        elif 'attachmentId' in part['body']:
            file_data = self.manager.get_attachment(self.message.message_id, part['body']['attachmentId'])
            if file_data:
                file_data = file_data.get('data')
            else:
                logger.warning('No attachment could be downloaded, not storing anything')
                return
        else:
            logger.warning('No attachment, not storing anything')
            return

        file_data = base64.urlsafe_b64decode(file_data.encode('UTF-8'))

        # Create as string file.
        file = StringIO.StringIO(file_data)
        if headers and 'content-type' in headers:
            file.content_type = headers['content-type'].split(';')[0]
        else:
            file.content_type = 'application/octet-stream'

        file.size = len(file_data)
        file.name = part.get('filename', '').rsplit('\\')[-1]
        if len(file.name) > 200:
            file.name = None

        # No filename in part, create a name.
        if not file.name:
            extensions = get_extensions_for_type(file.content_type)
            if part.get('partId'):
                file.name = 'attachment-%s%s' % (part.get('partId'), extensions.next())
            else:
                logger.warning('No part id, no filename')
                file.name = 'attachment-%s-%s' % (
                    len(self.attachments) + len(self.inline_attachments),
                    extensions.next()
                )

        final_file = File(file, file.name)

        # Create a EmailAttachment object.
        attachment = EmailAttachment()
        attachment.attachment = final_file
        attachment.size = file.size
        attachment.inline = inline
        attachment.tenant_id = self.manager.email_account.tenant_id

        # Check if inline attachment.
        if inline:
            attachment.cid = headers.get('content-id')

        self.attachments.append(attachment)

    def _create_body_html(self, body, encoding=None):
        """
        parse string to a correct coded html body part and add to Message.body_html

        Args:
            body (string): not encoded string
            encoding (string): possible encoding type
        """
        decoded_body = None

        # Use given encoding type
        if encoding:
            try:
                decoded_body = body.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                pass

        # BS4 decoding second
        if not decoded_body:
            soup = BeautifulSoup(body, 'lxml')
            if soup.original_encoding:
                encoding = soup.original_encoding
                try:
                    decoded_body = body.decode(encoding)
                except (LookupError, UnicodeDecodeError):
                    pass

        # If decoding fails, just force utf-8
        if not decoded_body and body:
            logger.warning('couldn\'t decode, forced utf-8 > %s' % self.message.message_id)
            encoding = 'utf-8'
            decoded_body = body.decode(encoding, errors='replace')

        # Only add if there is a body
        if decoded_body:
            self.message.body_html += decoded_body.encode(encoding).decode('utf-8')

    def _create_body_text(self, body, encoding=None):
        """
        parse string to a correct coded text body part and add to Message.body_text

        Args:
            body (string): not encoded string
            encoding (string): possible encoding type
        """
        decoded_body = None

        # Use given encoding type
        if encoding:
            try:
                decoded_body = body.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                pass

        # UnicodeDammit decoding second
        if not decoded_body:
            dammit = UnicodeDammit(body)
            if dammit.original_encoding:
                encoding = dammit.original_encoding
                try:
                    decoded_body = body.decode(encoding)
                except (LookupError, UnicodeDecodeError):
                    pass

        # If decoding fails, just force utf-8
        if not decoded_body and body:
            logger.warning('couldn\'t decode, forced utf-8 > %s' % self.message.message_id)
            encoding = 'utf-8'
            decoded_body = body.decode(encoding, errors='replace')

        if decoded_body:
            self.message.body_text += decoded_body.encode(encoding).decode('utf-8')

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

    def save(self):
        # Only save if there is a sent date, otherwise it's a chat message.
        if self.message.sent_date and self.message.sender_id:

            self.message.skip_signal = True  # Disable intermediate reindexing of the message.

            # Check for attachments.
            if self.attachments or self.inline_attachments:
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

    def _get_encoding_from_headers(self, headers):
        """
        Try to find encoding from headers

        Args:
            headers (list): of headers

        Returns:
            encoding or None: string with encoding type
        """
        headers = {name.lower(): value for name, value in headers.iteritems()}
        if 'content-type' in headers:
            for header_part in headers.get('content-type').split(';'):
                if 'charset' in header_part.lower():
                    return header_part.split('=')[-1].lower().strip('"\'')

        return None

    def _headers_to_dict(self, headers):
        """
        create dict from headers list

        Args:
            headers (list): of dicts with header info

        Returns:
            headers: dict with header_name : header_value
        """
        if headers:
            headers = {header['name']: header['value'] for header in headers}
        return headers

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
        self.inline_attachments = {}
