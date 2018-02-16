import base64

from email_wrapper_lib.providers.google.parsers.utils import parse_date_string, parse_recipient_string


def parse_message_list(data, promise=None):
    message_list = [message['id'] for message in data['messages']]

    if promise:
        promise.resolve(message_list)

    return message_list


def parse_message(data, promise=None):
    message = {}
    payload = data.get('payload', {})
    folders = data.get('labelIds', [])

    message.update({
        'remote_id': data['id'],
        'thread_id': data['threadId'],
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
    # message.update(parse_parts(payload))

    if promise:
        promise.resolve(message)

    return message


def parse_headers(data, promise=None):
    headers = {
        'recipients': {}
    }
    wanted_headers = [
        'subject',
        'date',
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

            if name == 'date':
                headers['received_date_time'] = parse_date_string(value)
            elif name == 'message_id':
                headers['mime_message_id'] = value.decode("unicode-escape")
            elif name in ['to', 'cc', 'bcc', 'from', 'sender', 'reply_to']:
                headers['recipients'][name] = parse_recipient_string(value)
            else:
                headers[name] = value

    if promise:
        promise.resolve(headers)

    return headers


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
