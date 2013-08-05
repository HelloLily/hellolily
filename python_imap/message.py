import email
import re
import StringIO
from email.header import decode_header
from email.utils import CRLF, ecre, EMPTYSTRING, fix_eols, getaddresses

import pytz
from bs4 import BeautifulSoup, UnicodeDammit
from dateutil.parser import parse
from dateutil.tz import tzutc

from logger import logger
from utils import convert_html_to_text, get_extensions_for_type


def decode_header_proper(value):
    if value is None:
        return None

    value = re.sub(ecre, r'=?\1?\2?\3?= ', value)

    value = fix_eols(value)
    value = re.sub(CRLF, EMPTYSTRING, value)

    header_fragments = []
    decoded_fragments = decode_header(value)
    for fragment, encoding in decoded_fragments:
        if encoding is None:
            dammit = UnicodeDammit(fragment)
            if dammit.original_encoding is not None:
                encoding = dammit.original_encoding
            else:
                encoding = 'utf-8'
        fragment = fragment.decode(encoding, 'replace')
        header_fragments.append(fragment)

    return ''.join(header_fragments)


def parse_sent_date(message, internaldate):
    sent_date = None

    if message is not None:
        received_headers = message.get_all('Received')
        date_header = message.get('Date')

        if received_headers is not None:
            for received_header in received_headers:
                received_date = received_header.split(';')[-1].strip()

                if sent_date is None or received_date < sent_date:
                    sent_date = received_date
        elif date_header is not None:
            sent_date = message.get('Date')

    if sent_date is not None:
        try:
            parsed = parse(sent_date)
            if parsed.tzinfo:
                parsed.tzinfo._name = None
            sent_date = parsed.astimezone(tzutc())
        except ValueError:
            sent_date = None

    if sent_date is None and internaldate is not None:
        sent_date = pytz.utc.localize(internaldate)

    return sent_date


def parse_headers(message):
    """
    Return cleaned headers for message, an instance of email.message.Message.
    """
    headers = dict(message.items())
    for name, value in headers.items():
        headers[name] = decode_header_proper(value)

    headers['Content-Type'] = message.get_content_type()

    return headers


def parse_body(message_part):
    """
    Returns content type and decoded message part.
    """
    content_type = message_part.get_content_type()
    payload = message_part.get_payload(decode=True)
    decoded_payload = None

    try:
        decoded_payload = payload.decode(message_part.get_content_charset())
    except:
        if content_type == 'text/html':
            soup = BeautifulSoup(payload)

            try:
                decoded_payload = payload.decode(soup.original_encoding)
            except:
                pass

    if decoded_payload is None and payload is not None:
        decoded_payload = payload.decode('utf-8', errors='replace')

    return content_type, decoded_payload


def parse_attachment(message_part, attachments, inline_attachments):
    """
    Return whether message_part contains attachment data.
    """
    attachment = {}

    # Don't show these content types as attachments
    if message_part.get_content_type() not in ['text/plain', 'text/html']:
        # Check for 'normal' attachments first
        if message_part.get('Content-Disposition', False):
            dispositions = message_part.get('Content-Disposition').strip().split(';')
            if dispositions[0].lower() in ['attachment', 'inline']:
                file_data = message_part.get_payload(decode=True)
                if file_data is not None:
                    attachment['name'] = message_part.get_filename()
                    attachment['size'] = len(file_data)
                    attachment['payload'] = file_data
                    attachment['content_type'] = message_part.get_content_type()

                    if attachment.get('name') is None:
                        count = len(attachments)
                        extensions = get_extensions_for_type(attachment.get('content_type'))
                        try:
                            name = 'attachment-%d%s' % (count, extensions.next())
                            attachment['name'] = name
                        except:
                            pass

                    if attachment.get('name') is not None:
                        logger.debug(message_part.get('Content-ID'))
                        logger.debug('%s is a normal attachment' % attachment['name'])
                        attachments.append(attachment)
                        return True
            else:
                logger.info('other disposition found: %s' % ';'.join(dispositions))

        # Check if it might be an inline attachment
        if attachment.get('payload') is None and message_part.get('Content-ID') is not None:
            file_data = message_part.get_payload(decode=True)
            if file_data is not None:
                attachment['cid'] = message_part.get('Content-ID')[1:-1]
                attachment['name'] = message_part.get_filename()
                attachment['size'] = len(file_data)
                attachment['payload'] = file_data
                attachment['content_type'] = message_part.get_content_type()

                if attachment.get('name') is None:
                    count = len(inline_attachments) + 1
                    extensions = get_extensions_for_type(attachment.get('content_type'))
                    try:
                        name = 'attachment-%d%s' % (count, extensions.next())
                        attachment['name'] = name
                    except:
                        pass

                if attachment.get('name') is not None:
                    logger.debug(message_part.get('Content-ID'))
                    logger.debug('%s is an inline attachment' % attachment['name'])
                    inline_attachments[attachment.get('cid')] = attachment
                    return True

    # Didn't find an attachment (with a name) so assume it's part of the body
    return False


def parse_message(message):
    """
    Parse an email.message.Message instance.
    """
    text = ''
    html = ''
    attachments = []
    inline_attachments = {}

    for message_part in message.walk():
        if message.get_content_maintype() == 'multipart':
            is_attachment = parse_attachment(message_part, attachments, inline_attachments)
            if is_attachment:
                continue

        if message_part is None:
            continue

        content_type, body = parse_body(message_part)
        if content_type == 'text/html':
            html += body
        elif content_type == 'text/plain':
            text += body
        elif not any([content_type, body]):
            continue

        if message_part.get_content_maintype() == 'multipart':
            continue

        if message_part.get('Content-Disposition') is None:
            continue

    if len(text) > 0:
        text = convert_html_to_text(text)

    if len(html) > 0 and len(inline_attachments) > 0:
        soup = BeautifulSoup(html)
        inline_images = soup.findAll('img', {'src': lambda src: src and src.startswith('cid:')})
        cids_in_body = []
        for image in inline_images:
            cids_in_body.append(image.get('src')[4:])

        for cid, inline_attachment in inline_attachments.items():
            if cid not in cids_in_body:
                del inline_attachments[cid]

    return text, html, attachments, inline_attachments


class Message(object):
    uid = None
    folder = None
    _imap_response = None
    _message = None
    _headers = None
    send_from = None
    recipients = None
    sent_date = None
    subject = None
    flags = None
    text = None
    html = None
    attachments = None
    inline_attachments = None
    size = None

    def __init__(self, imap_response, uid=None, folder=None):
        self.uid = uid
        self.folder = folder
        self._imap_response = imap_response

        message_string_key = 'BODY[]'
        for key in self._imap_response:
            if key.startswith('BODY[HEADER'):
                message_string_key = key

        message_string = self._imap_response.get(message_string_key, '')
        if len(message_string) > 0:
            self._message = email.message_from_string(message_string)

    def process(self):
        self.get_flags()
        self.get_headers()
        self.get_send_from()
        self.get_recipients()
        self.get_subject()
        self._parse_body()
        self.get_size()
        self.get_sent_date()

    def get_flags(self):
        if self.flags is None:
            if 'FLAGS' in self._imap_response:
                self.flags = self._imap_response.get('FLAGS')

        return self.flags

    def get_headers(self):
        if self._headers is None and self._message is not None:
            self._headers = parse_headers(self._message)

        return self._headers

    def get_send_from(self):
        if self.send_from is None:
            if self._headers is not None:
                from_header = self._headers.get('From')
            elif self._message is not None:
                from_header = decode_header_proper(self._message.get('From'))

            self.send_from = email.utils.parseaddr(from_header)

        return self.send_from

    def get_recipients(self):
        if self.recipients is None:
            self.get_headers()

            self.recipients = {}

            if self._headers is not None:
                to_recipients = None
                if self._headers.get('To') is not None:
                    to_recipients = getaddresses([self._headers.get('To')])
                elif 'Delivered-To' in self._headers:
                    to_recipients = getaddresses([self._headers.get('Delivered-To')])

                if to_recipients is not None:
                    self.recipients['to'] = to_recipients

                if self._headers.get('Cc') is not None:
                    self.recipients['cc'] = getaddresses([self._headers.get('Cc')])

                if self._headers.get('Bcc') is not None:
                    self.recipients['cc'] = getaddresses([self._headers.get('Bcc')])

        return self.recipients

    def get_subject(self):
        if self.subject is None and self._message is not None:
            self.subject = decode_header_proper(self._message.get('Subject'))

        return self.subject

    def _parse_body(self):
        if self._message is not None and 'BODY[]' in self._imap_response:
            text, html, attachments, inline_attachments = parse_message(self._message)

            self.text = text
            self.html = html
            self.attachments = attachments
            self.inline_attachments = inline_attachments

    def get_text_body(self):
        if self.text is None:
            self._parse_body()

        return self.text

    def get_html_body(self):
        if self.html is None:
            self._parse_body()

        return self.html

    def get_attachments(self):
        if self.attachments is None:
            self._parse_body()

        return self.attachments or []

    def get_inline_attachments(self):
        if self.inline_attachments:
            self._parse_body()

        return self.inline_attachments or {}

    def get_size(self):
        if self.size is None:
            if 'RFC822.SIZE' in self._imap_response:
                self.size = self._imap_response.get('RFC822.SIZE')

        return self.size

    def get_sent_date(self):
        if self.sent_date is None:
            self.sent_date = parse_sent_date(self._message, self._imap_response.get('INTERNALDATE', None))

        return self.sent_date
