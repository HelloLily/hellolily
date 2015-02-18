import logging
import base64
import email
import datetime
import gc
import StringIO

from bs4 import BeautifulSoup, UnicodeDammit
from dateutil.parser import parse
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import transaction
import pytz

from python_imap.utils import get_extensions_for_type

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
        Get or create Message.

        Arguments:
            message_dict (dict): with label information

        Returns:
            message (instance): unsaved message
            created (boolean): True if label is created
        """
        # Reset current builder info
        self.message = None
        self.labels = []
        self.headers = []
        self.received_by = set()
        self.received_by_cc = set()
        self.attachments = []
        self.inline_attachments = {}

        # Prevent memory leaks
        gc.collect()

        # Get or create without save
        created = False
        with transaction.atomic():
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
            self.message.thread_id = message_dict['threadId'],

        return self.message, created

    def store_message_info(self, message_info, message_id):
        """
        With given dict, create or update current message

        Args:
            message_info (dict): with message info
            message_id (string): message_id of email
        """
        self.get_or_create_message({'id': message_id})
        self.message.snippet = message_info['snippet']
        self.message.thread_id = message_info['threadId']

        # Save labels
        self.store_labels_for_message(message_info.get('labelIds', []), message_id)

        # Save the payload
        self._save_message_payload(message_info['payload'])

    def store_labels_for_message(self, labels, message_id):
        """
        Handle the labels for current Message

        Args:
            labels (list): of label_identifiers
            message_id (string): message_id of email
        """
        self.get_or_create_message({'id': message_id})

        # clear current labels
        if self.message.pk and self.message.labels:
            self.message.labels.clear()

        # UNREAD identifier check to see if message is read
        self.message.read = settings.GMAIL_UNREAD_LABEL not in labels

        # Store all labels
        for label in labels:
            # Do not save UNREAD_LABEL
            if label == settings.GMAIL_UNREAD_LABEL:
                continue

            db_label = self.manager.get_label(label)
            self.labels.append(db_label)

    def _save_message_payload(self, payload):
        """
        Walk trough message and save headers and parts

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
            header_name = header['name']
            header_value = header['value']
            if header_name == 'Date':
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
            elif header_name == 'Subject':
                self.message.subject = header_value
            elif header_name.lower() in ['to', 'from', 'cc', 'delivered-to']:
                self._create_recipients(header_name, header_value)
            else:
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
        # Check if part has child parts
        if 'parts' in part:
            for part in part['parts']:
                self._parse_message_part(part)
        else:
            part_headers = self._headers_to_dict(part.get('headers', {}))

            # Get content type
            mime_type = part['mimeType']

            # Check if part is an attachment
            if part['filename'] or 'data' not in part['body'] or mime_type == 'text/css':
                self._create_attachment(part, part_headers)

            # Handle non attachment
            else:
                # Decode body part
                body = base64.urlsafe_b64decode(part['body']['data'].encode())

                encoding = None
                if part_headers:
                    encoding = self._get_encoding_from_headers(part_headers)

                if mime_type == 'text/html':
                    self._create_body_html(body, encoding)

                elif mime_type == 'text/plain':
                    self._create_body_text(body, encoding)

                elif mime_type == 'text/xml':
                    # Conversation xml, do not store
                    pass
                elif mime_type == 'text/rfc822-headers':
                    # Header part, not needed
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
                    # attachments
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
        Create an attachment for the given part

        Args:
            part (dict): with attachment info
            headers (dict): headers for message part

        Raises:
            Attachment exception if attachment couldn't be created
        """
        logger.debug('Storing attachment for message %s' % self.message.message_id)
        headers = {name.lower(): value for name, value in headers.iteritems()}

        # Check if attachment is inline
        inline = False
        if headers and headers.get('content-id', False):
            inline = True

        # Get file data from part or from remote
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

        # create as string file
        file = StringIO.StringIO(file_data)
        if headers and 'content-type' in headers:
            file.content_type = headers['content-type']
        else:
            file.content_type = 'application/octet-stream'

        file.size = len(file_data)
        file.name = part.get('filename', '')

        # No filename in part, create a name
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

        # Create a EmailAttachment object
        attachment = EmailAttachment()
        attachment.attachment = final_file
        attachment.size = file.size
        attachment.inline = inline
        attachment.tenant_id = self.manager.email_account.tenant_id

        # Check if inline attachment
        if inline:
            self.inline_attachments[headers.get('content-id')] = attachment
        else:
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
            except (LookupError, UnicodeDecodeError) as e:
                pass

        # BS4 decoding second
        if not decoded_body:
            soup = BeautifulSoup(body)
            if soup.original_encoding:
                encoding = soup.original_encoding
                try:
                    decoded_body = body.decode(encoding)
                except (LookupError, UnicodeDecodeError) as e:
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
                except (LookupError, UnicodeDecodeError) as e:
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
        header_value = header_value.lower()

        # Get or create recipient
        email_address = email.utils.parseaddr(header_value)
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

    def _place_inline_attachments(self):
        """
        Try to replace the cid src for a url to the attachment

        TODO: make url look fancy with filename
        """
        if not self.message.body_html:
            return

        for key, attachment in self.inline_attachments.iteritems():
            key = key[1:-1]
            src = reverse('email_attachment_proxy_view', kwargs={'pk': attachment.pk})
            self.message.body_html = self.message.body_html.replace('cid:%s' % key, src)

    def save(self):
        # Only save if there is a sent date, otherwise its a chat message
        if self.message.sent_date and self.message.sender_id:

            # Check for attachments
            if self.attachments or self.inline_attachments:
                self.message.has_attachment = True

            # Save before we can add many to many and foreign keys
            self.message.save()

            # Save recipients
            self.message.received_by.add(*self.received_by)
            self.message.received_by_cc.add(*self.received_by_cc)

            # Save labels
            for label in self.labels:
                label.save()
                self.message.labels.add(label)

            # Save headers
            for header in self.headers:
                self.message.headers.add(header)

            # Save attachments
            for attachment in self.attachments:
                self.message.attachments.add(attachment)

            # Save inline attachments
            if self.inline_attachments:
                for attachment in self.inline_attachments.itervalues():
                    self.message.attachments.add(attachment)
                self._place_inline_attachments()
                # We've changed the body_html, lets save message one more time
                self.message.save()
        else:
            logger.debug('No emailmessage, storing empty ID')
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
