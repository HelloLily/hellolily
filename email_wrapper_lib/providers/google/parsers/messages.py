import base64
from datetime import datetime
from pytz import utc

from email_wrapper_lib.providers.google.parsers.utils import parse_recipient_string


def parse_message_list(data, promise=None):
    parsed = {}

    # Google can return an empty page as last page, so check if we got any data at all.
    if data:
        parsed = {
            'messages': [message['id'] for message in data.get('messages', [])],
            'next_page_token': data.get('nextPageToken', None),
        }

    if promise:
        promise.resolve(parsed)

    return parsed


def parse_message_full(data, promise=None):
    payload = data.get('payload', {})
    message = parse_message(data)

    message.update(parse_parts(payload))

    if promise:
        promise.resolve(message)

    return message


def parse_message_minimal(data, promise=None):
    payload = data.get('payload', {})
    message = parse_message(data)

    message['has_attachments'] = check_attachments(payload)

    if promise:
        promise.resolve(message)

    return message


def parse_message_folders(data, promise=None):
    folders = data.get('labelIds', [])
    message = {
        'remote_id': data['id'],
        'thread_id': data['threadId'],
        'folders': folders,
        'is_read': 'UNREAD' not in folders,
        'is_starred': 'STARRED' in folders,
    }

    if promise:
        promise.resolve(message)

    return message


def parse_message(data, promise=None):
    message = {}
    payload = data.get('payload', {})
    folders = data.get('labelIds', [])

    # Google gives us epoch in milliseconds, python needs it in seconds, that's why we divide by 1000.
    internal_date = int(data['internalDate']) / 1000

    message.update({
        'remote_id': data['id'],
        'thread_id': data['threadId'],
        'received_date_time': datetime.fromtimestamp(internal_date, utc),
        'folders': folders,
        'snippet': data['snippet'],
        'is_read': 'UNREAD' not in folders,
        'is_starred': 'STARRED' in folders,
        # 'is_draft': 'DRAFT' in folders,
        # 'is_important': 'IMPORTANT' in folders,
        # 'is_archived': 'ARCHIVED' in folders,
        # 'is_trashed': 'TRASH' in folders,
        # 'is_spam': 'SPAM' in folders,
        # 'is_chat': 'CHAT' in folders,
    })

    message.update(parse_headers(payload.get('headers', [])))

    if promise:
        promise.resolve(message)

    return message


def parse_headers(data, promise=None):
    headers = {
        'recipients': {}
    }
    wanted_headers = [
        'subject',
        # 'date',
        'from',
        'sender',
        'reply_to',
        'to',
        'cc',
        'bcc',
        'message_id',
    ]

    for header in data:
        name = header.get('name').lower().replace('-', '_')

        if name in wanted_headers:
            value = header.get('value')

            # if name == 'date':
            #     headers['received_date_time'] = parse_date_string(value)

            if name == 'message_id':
                headers['mime_message_id'] = value.decode("unicode-escape")
            elif name in ['to', 'cc', 'bcc', 'from', 'sender', 'reply_to']:
                headers['recipients'][name] = parse_recipient_string(value)
            else:
                headers[name] = value

    if promise:
        promise.resolve(headers)

    return headers


def check_attachments(data, promise=None):
    has_attachments = False
    if 'parts' in data:
        # This message is multipart.
        for sub_part in data.get('parts'):
            has_attachments = check_attachments(sub_part)
            if has_attachments:
                break
    elif 'filename' in data or data.get('mimeType') == 'text/css':
        has_attachments = True

    if promise:
        promise.resolve(has_attachments)

    return has_attachments


def parse_parts(data, promise=None):
    parts = {
        'body_text': '',
        'body_html': '',
        'has_attachments': False,
        'attachments': [],
    }

    if 'parts' in data:
        # This message is multipart.
        for sub_part in data.get('parts'):
            parts.update(parse_parts(sub_part))
    else:
        mimetype = data.get('mimeType')
        body_data = data.get('body', {}).get('data', '').encode()

        if mimetype == 'text/plain':
            parts['body_text'] = base64.urlsafe_b64decode(body_data)
        elif mimetype == 'text/html':
            parts['body_html'] = base64.urlsafe_b64decode(body_data)
        elif 'filename' in data or mimetype == 'text/css':
            parts['has_attachments'] = True
            parts['attachments'].append(parse_attachment(data))

    if promise:
        promise.resolve(parts)

    return parts


def parse_attachment(data, promise=None):
    attachment = {
        'remote_id': data.get('body', {}).get('attachmentId', ''),
        'mimetype': data.get('mimeType', ''),
        'filename': data.get('filename', ''),
        'inline': False,
    }

    # Attachments have their own headers.
    headers = parse_headers(data.get('headers', {}))

    if headers.get('content_id', False):
        attachment['inline'] = True

    if promise:
        promise.resolve(attachment)

    return attachment
