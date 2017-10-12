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


def parse_profile(data, profile):
    profile.update({
        'user_id': data['emailAddress'],
        'username': data['emailAddress'],
        'history_token': data['historyId'],
    })

    return profile


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
            folder_ids = change.get('labelIds')

            for label in folder_ids:
                try:
                    history['deleted_labels'][remote_id].remove(label)
                except ValueError:
                    history['added_labels'][remote_id].append(label)

        for change in history_item.get('labelsRemoved', []):
            remote_id = change.get('message').get('id')
            folder_ids = change.get('labelIds')

            for label in folder_ids:
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
    messages['messages'] = {}

    # Because Google only gives message ids, we need to do a second batch for the bodies.
    for remote_id in message_list:
        messages['messages'][remote_id].append(message_resource.get(remote_id))

    message_resource.batch.execute()

    messages['history_token'] = messages['messages'][0].get('history_token')
    messages['page_token'] = data.get('nextPageToken')

    return messages


def parse_message(data, message):
    payload = data.get('payload', {})
    folder_ids = data.get('labelIds')

    message.update({
        'remote_id': data['id'],
        'thread_id': data['threadId'],
        'history_token': data['historyId'],
        'folder_ids': folder_ids,  # TODO: Should the key not be called label_ids?
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

    return message


def parse_date_string(data):
    # TODO: try to use the tuple in an easier way using time.mktime

    # Try it the most simple way.
    datetime_tuple = parsedate_tz(data)
    if datetime_tuple:
        return datetime.fromtimestamp(mktime_tz(datetime_tuple), pytz.UTC)
    else:
        return parse(data)


def parse_recipient_string(data):
    return [{
        'name': recipient[0],
        'email_address': recipient[1],
    } for recipient in getaddresses([data])]


def parse_headers(data):
    header_dict = {}  # TODO: rename, it gets the data from the headers, but is afterwards it aren't headers anymore.
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

            header_dict.update({
                name: value
            })

    return header_dict


def parse_parts(data):
    parts_dict = {
        'body_text': '',
        'body_html': '',
        'has_attachments': False,
        'attachments': [],
    }

    if 'parts' in data:
        # This message is multipart.
        for sub_part in data.get('parts'):
            parts_dict.update(parse_parts(sub_part))
    else:
        mimetype = data.get('mimeType')
        body_data = data.get('body', {}).get('data', '').encode()

        if mimetype == 'text/plain':
            parts_dict['body_text'] = base64.urlsafe_b64decode(body_data)
        elif mimetype == 'text/html':
            parts_dict['body_html'] = base64.urlsafe_b64decode(body_data)
        elif 'filename' in data or mimetype == 'text/css':
            parts_dict['has_attachments'] = True
            parts_dict['attachments'].append(parse_attachment(data))

    return parts_dict


def parse_attachment(data):
    attachment_dict = {
        'id': data.get('body', {}).get('attachmentId', ''),
        'mimetype': data.get('mimeType', ''),
        'filename': data.get('filename', ''),
        'inline': False,
    }

    # Attachments have their own headers.
    headers = parse_headers(data.get('headers', {}))

    if headers.get('content_id', False):
        attachment_dict['inline'] = True

    return attachment_dict


def parse_label_list(data, labels, label_resource):
    # Because google only gives partial labels, we need to do a second batch for more info.
    for label in data.get('labels', []):
        labels[label['id']] = label_resource.get(label['id'])

    label_resource.batch.execute()

    return labels


def parse_label(data, label):
    label.update({
        'id': data['id'],
        'name': data['name'].split('/')[-1:],
        'remote_value': data['name'],
        'message_count': data['messagesTotal'],
        'unread_count': data['messagesUnread'],
        'folder_type': data['type'],
        'parent_id': None,
    })

    # TODO: how do we find the parent id here?

    return label
