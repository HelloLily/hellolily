import base64
import pytz
from collections import defaultdict
from email.utils import getaddresses, parsedate_tz, mktime_tz
from datetime import datetime
from dateutil.parser import parse

from email_wrapper_lib.providers.exceptions import BatchRequestException


def parse_response(callback_func, *args, **kwargs):
    def transform(request_id, response, exception):
        if exception:
            raise BatchRequestException(exception)
        else:
            callback_func(response, *args, **kwargs)

    return transform


def parse_history(data, history, message_resource):
    history_list = data.get('history', [])
    messages = {'messages': []}  # Conform the output of google's list, to be parsed by parse_message_list.
    history.update({
        'history_token': None,
        'page_token': None,
        'added_labels': defaultdict(list),
        'deleted_labels': defaultdict(list),
        'added_messages': [],
        'deleted_messages': [],
    })

    for history_item in history_list:
        for message in history_item.get('messagesAdded', []):
            messages['messages'].append({
                'id': message.get('message').get('id'),
                'threadId': message.get('message').get('threadId')
            })

        for message in history_item.get('messagesDeleted', []):
            history['deleted_messages'].append(message.get('message').get('id'))

        # When users add and remove labels, it will show up as seperate items in the history.
        # That's why we first check if the user has done the opposite action, because it would cancel out.

        for change in history_item.get('labelsAdded', []):
            remote_id = change.get('message').get('id')
            label_ids = change.get('labelIds')

            for label in label_ids:
                try:
                    history['deleted_labels'][remote_id].remove(label)
                except ValueError:
                    history['added_labels'][remote_id].append(label)

        for change in history_item.get('labelsRemoved', []):
            remote_id = change.get('message').get('id')
            label_ids = change.get('labelIds')

            for label in label_ids:
                try:
                    history['added_labels'][remote_id].remove(label)
                except ValueError:
                    history['deleted_labels'][remote_id].append(label)

    parsed_messages = {}
    parse_message_list(messages, parsed_messages, message_resource)
    history['added_messages'] = parsed_messages['messages']

    history['history_token'] = data.get('historyId')
    history['page_token'] = data.get('nextPageToken')

    return history


def parse_message_list(data, messages, message_resource):
    message_list = [message.get('id') for message in data.get('messages', [])]
    messages['messages'] = []

    # Because google only gives message ids, we need to do a second batch for the bodies.
    for remote_id in message_list:
        messages['messages'].append(message_resource.get(remote_id))

    message_resource.batch.execute()

    messages['history_token'] = messages['messages'][0].get('history_token')
    messages['page_token'] = data.get('nextPageToken')

    return messages


def parse_message(data, message):
    payload = data.get('payload', {})
    label_ids = data.get('labelIds')
    headers = parse_headers(payload.get('headers', []))

    message.update({
        'remote_id': data['id'],
        'thread_id': data['threadId'],
        'history_token': data['historyId'],
        'labels_ids': label_ids,
        'snippet': data['snippet'],
        'headers': headers,
        'is_read': 'READ' in label_ids,
        'is_starred': 'STARRED' in label_ids,
        'is_draft': 'DRAFT' in label_ids,
        'is_important': 'IMPORTANT' in label_ids,
        'is_archived': 'ARCHIVED' in label_ids,
        'is_trashed': 'TRASH' in label_ids,
        'is_spam': 'SPAM' in label_ids,
        'is_chat': 'CHAT' in label_ids,
    })

    header_shortcuts = [
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

    for shortcut in header_shortcuts:
        message[shortcut] = headers.get(shortcut)

    message.update(parse_parts(payload))

    return message


def parse_date_string(value):
    # TODO: try to use the tuple in an easier way using time.mktime

    # Try it the most simple way.
    datetime_tuple = parsedate_tz(value)
    if datetime_tuple:
        return datetime.fromtimestamp(mktime_tz(datetime_tuple), pytz.UTC)
    else:
        return parse(value)


def parse_recipient_string(value):
    return [{
        'name': recipient[0],
        'email_address': recipient[1]
    } for recipient in getaddresses([value])]


def parse_headers(header_json):
    header_dict = {}

    for header in header_json:
        name = header.get('name').lower().replace('-', '_')
        value = header.get('value')

        if name == 'date':
            value = parse_date_string(value)
        elif name == 'message_id':
            value = value.decode("unicode-escape")
        elif name in ['from', 'sender', 'reply_to', ]:
            recipient_list = parse_recipient_string(value)
            value = recipient_list[0] if recipient_list else {}
        elif name in ['to', 'cc', 'bcc']:
            value = parse_recipient_string(value)

        header_dict.update({
            name: value
        })

    return header_dict


def parse_parts(part_json):
    parts_dict = {
        'body_text': '',
        'body_html': '',
        'has_attachments': False,
        'attachments': [],
    }

    if 'parts' in part_json:
        # This message is multipart.
        for sub_part in part_json.get('parts'):
            parts_dict.update(parse_parts(sub_part))
    else:
        mimetype = part_json.get('mimeType')

        if part_json.get('mimeType') == 'text/plain':
            data = part_json.get('body', {}).get('data', '').encode()
            parts_dict['body_text'] = base64.urlsafe_b64decode(data)
        elif part_json.get('mimeType') == 'text/html':
            data = part_json.get('body', {}).get('data', '').encode()
            parts_dict['body_html'] = base64.urlsafe_b64decode(data)
        elif part_json.get('filename') or mimetype == 'text/css':
            parts_dict['has_attachments'] = True
            parts_dict['attachments'].append(parse_attachment(part_json))

    return parts_dict


def parse_attachment(attachment_json):
    attachment_dict = {
        'id': attachment_json.get('body', {}).get('attachmentId', ''),
        'mimetype': attachment_json.get('mimeType', ''),
        'filename': attachment_json.get('filename', ''),
        'inline': False,
    }

    # Attachments have their own headers.
    headers = parse_headers(attachment_json.get('headers', {}))

    if headers.get('content_id', False):
        attachment_dict['inline'] = True

    return attachment_dict
