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
    folder_ids = data.get('labelIds')

    message.update({
        'remote_id': data['id'],
        'thread_id': data['threadId'],
        'history_token': data['historyId'],
        'folder_ids': folder_ids,
        'snippet': data['snippet'],
        'is_read': 'UNREAD' not in folder_ids,
        'is_starred': 'STARRED' in folder_ids,
        'is_draft': 'DRAFT' in folder_ids,
        'is_important': 'IMPORTANT' in folder_ids,
        'is_archived': 'ARCHIVED' in folder_ids,
        'is_trashed': 'TRASH' in folder_ids,
        'is_spam': 'SPAM' in folder_ids,
        'is_chat': 'CHAT' in folder_ids,
    })

    message.update(parse_headers(payload.get('headers', [])))
    message.update(parse_parts(payload))

    if promise:
        promise.resolve(message)

    return message


def parse_headers(data, promise=None):
    headers = {}
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
                value = parse_date_string(value)
            elif name == 'message_id':
                value = value.decode("unicode-escape")
            elif name in ['from', 'sender', 'reply_to', ]:
                recipient_list = parse_recipient_string(value)
                value = recipient_list[0] if recipient_list else {}
            elif name in ['to', 'cc', 'bcc', ]:
                value = parse_recipient_string(value)

            headers.update({
                name: value
            })

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
