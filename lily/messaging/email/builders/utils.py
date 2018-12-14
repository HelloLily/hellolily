import base64
import re
import logging
import StringIO

from django.core.files import File
from bs4 import BeautifulSoup, UnicodeDammit
from lily.messaging.email.utils import get_extensions_for_type

from ..models.models import EmailAttachment

logger = logging.getLogger(__name__)

ATTACHMENT_MIME_TYPES = (
    'text/css',
    'application/octet-stream',
    'image/gif',
    'image/jpg',
    'image/x-png',
    'image/png',
    'image/jpeg',
)

NON_ATTACHMENT_MIME_TYPES = (
    'text/html',
    'text/plain',
    'text/xml',
    'text/rfc822-headers'
)


def get_attachments_from_payload(payload, body_html, message_id, connector):
    """
    Return a list of attachments that are created by extracting information from the payload.

    Args:
        payload (dict): with attachment info
        body_html (string): body that could contain references to attachments
        message_id (string): containing a reference to the message stored on Gmail
        connector (GmailConnector): active connector to communicate with Gmail

    Returns:
        attachments (list): list of attachments
    """
    attachments = []
    append_attachments_from_payload(payload, body_html, message_id, attachments, connector)
    return attachments


def append_attachments_from_payload(payload, body_html, message_id, attachments, connector):
    """
    Appends to the given attachments the attachments that are created by extracting information from the payload.

    Args:
        payload (dict): with attachment info
        body_html (string): body that could contain references to attachments
        message_id (string): containing a reference to the message stored on Gmail
        attachments (list): list of attachments previously created for naming purposes
        connector (GmailConnector): active connector to communicate with Gmail

    Returns:
        attachments (list): list of attachment
    """
    if 'parts' in payload:
        for part in payload['parts']:
            append_attachments_from_payload(part, body_html, message_id, attachments, connector)

    if payload['mimeType'] in NON_ATTACHMENT_MIME_TYPES:
        return attachments

    attachment = create_attachment(payload, body_html, message_id, attachments, connector)

    if not attachment:
        return attachments

    attachments.append(attachment)
    if not (payload['filename'] or 'data' not in payload['body'] or payload['mimeType'] in ATTACHMENT_MIME_TYPES):
        logging.warning('other mime_type %s for message %s, account %s' % (
            payload['mimeType'],
            message_id,
            connector.email_account,
        ))

    return attachments


def create_attachment(part, body_html, message_id, attachments, connector):
    """
    Create and add attachment to the given attachments for the given part.

    Args:
        part (dict): with attachment info
        body_html (string): body that could contain references to attachments
        message_id (string): containing a reference to the message stored on Gmail
        attachments (list): list of attachments previously created for naming purposes
        connector (GmailConnector): active connector to communicate with Gmail

    Returns:
        attachment (EmailAttachment)

    Raises:
        Attachment exception if attachment couldn't be created.
    """
    logger.debug('Storing attachment for message %s' % message_id)
    headers = get_headers_from_payload(part)
    headers = {name.lower(): value for name, value in headers.iteritems()}

    # Check if attachment is inline.
    inline = bool(headers and headers.get('content-id', False))

    if headers and 'content-disposition' in headers:
        # If 'content-disposition' is present it supersedes inline determination by just the 'content-id'.
        cd = headers['content-disposition'].split(';')[0].lower()
        if cd == 'inline' and 'content-id' in headers:
            # However there is still a chance that the content is incorrectly marked as inline. Look if there is a
            # reference to the cid in the body.
            body = body_html
            cid = headers.get('content-id')
            match = re.match(r"<(.*)>", cid)
            if match:
                # Removes surrounding <> from cid.
                cid = match.group(1)

            # Look if the cid is in the body html.
            inline = re.search("cid:{0}".format(cid), body) is not None

    # Get file data from part or from remote.
    if 'data' in part['body']:
        file_data = part['body']['data']
    elif 'attachmentId' in part['body']:
        file_data = connector.get_attachment(message_id, part['body']['attachmentId'])
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
            file.name = 'attachment-{}-0'.format(len(attachments), extensions.next())

    # Create a EmailAttachment object.
    attachment = EmailAttachment()
    attachment.attachment = File(file, file.name)
    attachment.size = file.size
    attachment.inline = inline
    attachment.tenant_id = connector.email_account.tenant_id

    # Check if inline attachment.
    if inline:
        attachment.cid = headers.get('content-id')

    return attachment


def get_headers_from_payload(part):
    """
    Return header dict from payload.

    Args:
        part (dict): from message payload

    Returns:
        headers: dict with header_name : header_value
    """
    headers = part.get('headers', {})

    if headers:
        headers = {header['name']: header['value'] for header in headers}

    return headers


def create_body_html(body, message_id, encoding=None):
    """
    Return correctly coded html body given a string.

    Args:
        body (string): not encoded string
        message_id (string): containing a reference to the message stored on Gmail
        encoding (string): possible encoding type
    """
    decoded_body = None

    # Use given encoding type.
    if encoding:
        try:
            decoded_body = body.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            pass

    # BS4 decoding second.
    if not decoded_body:
        soup = BeautifulSoup(body, 'lxml')
        if soup.original_encoding:
            encoding = soup.original_encoding
            try:
                decoded_body = body.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                pass

    # If decoding fails, just force utf-8.
    if not decoded_body and body:
        logger.warning('couldn\'t decode, forced utf-8 > %s' % message_id)
        encoding = 'utf-8'
        decoded_body = body.decode(encoding, errors='replace')

    # Only add if there is a body.
    if decoded_body:
        return decoded_body.encode(encoding).decode('utf-8', errors='replace')

    return ''


def create_body_text(body, message_id, encoding=None):
    """
    Return correctly coded text body given a string.

    Args:
        body (string): not encoded string
        encoding (string): possible encoding type
    """
    decoded_body = None

    # Use given encoding type.
    if encoding:
        try:
            decoded_body = body.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            pass

    # UnicodeDammit decoding second.
    if not decoded_body:
        dammit = UnicodeDammit(body)
        if dammit.original_encoding:
            encoding = dammit.original_encoding
            try:
                decoded_body = body.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                pass

    # If decoding fails, just force utf-8.
    if not decoded_body and body:
        logger.warning('couldn\'t decode, forced utf-8 > %s' % message_id)
        encoding = 'utf-8'
        decoded_body = body.decode(encoding, errors='replace')

    if decoded_body:
        return decoded_body.encode(encoding).decode('utf-8', errors='replace')

    return ''


def get_body_html_from_payload(payload, message_id):
    """
    Return body html given a payload.

    Args:
        payload (dict): with info about the body
        message_id (string): containing a reference to the message stored on Gmail
    """
    body_html = ''
    if 'parts' in payload:
        for part in payload['parts']:
            body_html += get_body_html_from_payload(part, message_id)

    headers = get_headers_from_payload(payload)
    if payload['mimeType'] == 'text/html':
        body = base64.urlsafe_b64decode(payload['body']['data'].encode())
        encoding = get_encoding_from_headers(headers)
        body_html += create_body_html(body, message_id, encoding)

    return body_html


def get_body_text_from_payload(payload, message_id):
    """
    Return body text given a payload.

    Args:
        payload (dict): with info about the body
        message_id (string): containing a reference to the message stored on Gmail
    """
    body_text = ''
    if 'parts' in payload:
        for part in payload['parts']:
            body_text += get_body_text_from_payload(part, message_id)

    headers = get_headers_from_payload(payload)
    if payload['mimeType'] == 'text/plain':
        body = base64.urlsafe_b64decode(payload['body']['data'].encode())
        encoding = get_encoding_from_headers(headers)
        body_text += create_body_text(body, message_id, encoding)

    return body_text


def get_encoding_from_headers(headers):
    """
    Try to find encoding from headers

    Args:
        headers (list): of headers

    Returns:
        encoding or None: string with encoding type
    """
    headers = get_headers_from_payload(headers)

    if not headers:
        return None

    headers = {name.lower(): value for name, value in headers.iteritems()}
    if 'content-type' in headers:
        for header_part in headers.get('content-type').split(';'):
            if 'charset' in header_part.lower():
                return header_part.split('=')[-1].lower().strip('"\'')

    return None
