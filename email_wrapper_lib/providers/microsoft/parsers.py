import urlparse

import re

from email_wrapper_lib.providers.exceptions import BatchRequestException
from microsoft_mail_client.constants import SYSTEM_FOLDERS_NAMES, FOLDER_ARCHIVE_NAME, FOLDER_DELETED_ITEMS_NAME, \
    FOLDER_JUNK_NAME, IMPORTANCE_HIGH


def parse_response(callback_func, *args, **kwargs):
    def transform(request_id, response, exception):
        if exception:
            raise BatchRequestException(exception)
        else:
            callback_func(response, *args, **kwargs)

    return transform


def parse_profile(data, profile):
    """
    {u'@odata.context': u'https://outlook.office.com/api/v2.0/$metadata#Users/$entity',
     u'@odata.id': u"https://outlook.office.com/api/v2.0/Users('00034001')",
     u'Alias': u'puid-0003400103F9ED36',
     u'DisplayName': u'Arjen Vellinga',
     u'EmailAddress': u'arjenfvellinga@outlook.com',
     u'Id': u'00034001-03f9-ed36-0000-000000000000@84df9e7f-e9f6-40af-b435-aaaaaaaaaaaa',
     u'MailboxGuid': u'00034001-03f9-ed36-0000-000000000000'}
    """
    data = data.json()
    profile.update({
        'user_id': data['EmailAddress'],
        'username': data['DisplayName'],
    })
    return profile


def parse_history(data, history, message_resource):
    data = data.json()
    return history


def parse_message_list(data, messages):
    data = data.json()
    messages['messages'] = {}

    # Retrieve dict with 3 (key, value) pairs to map folders from remote_id to Archive, Trash and Junk.
    # result = EmailFolder.objects.filter()  # TODO: implement right query.
    # TODO: implement mapping ParentFolderId: DisplayName label
    folders = {'xyz': 'Junk Email', 'uvw': 'Archive', 'abc': 'Deleted Items'}

    for message in data.get('value', []):
        messages['messages'][message['InternetMessageId']] = {  # Don't use Id, because it changes with folder mutations.
            'remote_id': message['InternetMessageId'],  # TODO: dubbelop so remove?
            'thread_id': message['ConversationId'],
            'history_token': '',  # TODO: Needed?
            'folder_ids': [message['ParentFolderId']],
            'snippet': message['BodyPreview'],
            'is_read': message['IsRead'],
            'is_starred': False,  # TODO: maybe 'pinned' messages? But available via API?
            'is_draft': message['IsDraft'],
            'is_important': message['Importance'] is IMPORTANCE_HIGH,
            'is_archived': message['ParentFolderId'] in folders and folders[message['ParentFolderId']] is FOLDER_ARCHIVE_NAME,
            'is_trashed': message['ParentFolderId'] in folders and folders[message['ParentFolderId']] is FOLDER_DELETED_ITEMS_NAME,
            'is_spam': message['ParentFolderId'] in folders and folders[message['ParentFolderId']] is FOLDER_JUNK_NAME,
            'is_chat': False,
        }

        # TODO: 'from', 'sender', 'reply_to', 'to', 'cc', 'bcc'.

    messages['page_token'] = None
    # Or are there more pages with messages?
    if '@odata.nextLink' in data:
        odata_next_link = data.get('@odata.nextLink')

        # Extract paging parameter from the odata next link.
        skip = urlparse.parse_qs(urlparse.urlparse(odata_next_link).query).get('$skip')[0]

        messages['page_token'] = skip

    return messages


def parse_message(data, message):
    """
    A message that changes from folder, gets a new ID, but InternetMessageId stays with every mutation the same.
    ParentFolderId can tell if it is archived, trashed, or spam.
    """
    data = data.json()
    # Retrieve dict with 3 (key, value) pairs to map folders from remote_id to Archive, Trash and Junk.
    # result = EmailFolder.objects.filter()  # TODO: implement right query.
    # TODO: implement mapping ParentFolderId: DisplayName label
    folders = {'xyz': 'Junk Email', 'uvw': 'Archive', 'abc': 'Deleted Items'}

    message.update({
        'remote_id': data['InternetMessageId'],  # Don't use Id, because it changes with folder mutations.
        'thread_id': data['ConversationId'],
        'history_token': '',  # TODO: Needed?
        'folder_ids': [data['ParentFolderId']],
        'snippet': data['BodyPreview'],
        'is_read': data['IsRead'],
        'is_starred': False,  # TODO: maybe 'pinned' messages? But available via API?
        'is_draft': data['IsDraft'],
        'is_important': data['Importance'] is IMPORTANCE_HIGH,
        'is_archived': data['ParentFolderId'] in folders and folders[data['ParentFolderId']] is FOLDER_ARCHIVE_NAME,
        'is_trashed': data['ParentFolderId'] in folders and folders[data['ParentFolderId']] is FOLDER_DELETED_ITEMS_NAME,
        'is_spam': data['ParentFolderId'] in folders and folders[data['ParentFolderId']] is FOLDER_JUNK_NAME,
        'is_chat': False,
    })

    # TODO: 'from', 'sender', 'reply_to', 'to', 'cc', 'bcc'.

    return message


def parse_label_list(data, labels, label_resource):
    """
    {u'@odata.context': u"https://outlook.office.com/api/v2.0/$metadata#Users('a%40outlook.com')/MailFolders",
    u'value': [{
    u'@odata.id': u"https://outlook.office.com/api/v2.0/Users('00034001')/MailFolders('AQMkADAwATM0MDAA')",
    u'ChildFolderCount': 0,
    u'DisplayName': u'Archive',
    u'Id': u'AQMkADAwATM0MDAAMS0wM2Y5LWVkMzYtMDACLTAwCgAuAAAD-Gudm_S5tkO5xIN4NveiEQEACQ2NI6ATzEGeCYmilLYoVgAAAgFOAAAA',
    u'ParentFolderId': u'AQMkADAwATM0MDAAMS0wM2Y5LWVkMzYtM',
    u'TotalItemCount': 0,
    u'UnreadItemCount': 0}]}
    """
    data = data.json()
    intermediate_list = []  # Necessary container to store the results of the delayed api execution.

    for label in data.get('value', []):
        labels[label['Id']] = {
            'id': label['Id'],
            'name': label['DisplayName'],
            'remote_value': label['DisplayName'],
            'message_count': label['TotalItemCount'],
            'unread_count': label['UnreadItemCount'],
            'folder_type': 'SYSTEM' if label['DisplayName'] in SYSTEM_FOLDERS_NAMES else 'USER',  # TODO: Correct values?
            'parent_id': label['ParentFolderId'],  # TODO: remote_id or our db id?
            'children': [],
        }

        if label['ChildFolderCount'] > 0:
            labels[label['Id']]['children'].append(label_resource.list(label_id=label['Id']))

    # Are there more pages with labels on the current level?
    if '@odata.nextLink' in data:
        odata_context = data.get('@odata.context')
        odata_next_link = data.get('@odata.nextLink')

        # Extract current label from the odata context.
        current_label_id = None
        regex = re.search(r'MailFolders\((.*?)\)', odata_context)
        if regex:
            current_label_id = regex.group(1)

        # Extract paging parameter from the odata next link.
        skip = urlparse.parse_qs(urlparse.urlparse(odata_next_link).query).get('$skip')[0]

        # Call and add next page with labels.
        intermediate_list.append(label_resource.list(label_id=current_label_id, skip=skip))

    if not label_resource.batch.empty:
        # Retrieve child labels / the next page with labels.
        label_resource.batch.execute()
        # Add them to the current labels.
        for intermediate_labels in intermediate_list:
            labels.update(intermediate_labels)

    return labels


def parse_label(data, label):
    """
    {u'@odata.context': u"https://outlook.office.com/api/v2.0/$metadata#Users('a%40outlook.com')/MailFolders/$entity",
     u'@odata.id': u"https://outlook.office.com/api/v2.0/Users('00034001')/MailFolders('AQMkADAwATM0MDAAMS0wM2Y5')",
     u'ChildFolderCount': 15,
     u'DisplayName': u'Inbox',
     u'Id': u'AQMkADAwATM0MDAAMS0wM2Y5LWVkMzYtMDACLTAwCgAuAAAD-Gudm_S5tkO5xI4NveiEQEACQ2NI6ATzEGeCYmilLYoVgAAAgEMAAAA',
     u'ParentFolderId': u'AQMkADAwATM0MDAAMS0wM2Y5LWVkMzYtMDACLTAwCgAuAAAD-NNveiEQEACQ2NI6ATzEGeCYmilLYoVgAAAgEIAAAA',
     u'TotalItemCount': 19,
     u'UnreadItemCount': 8}
     """
    data = data.json()

    label.update({
        'id': data['Id'],
        'name': data['DisplayName'],
        'remote_value': data['DisplayName'],
        'message_count': data['TotalItemCount'],
        'unread_count': data['UnreadItemCount'],
        'folder_type': 'SYSTEM' if data['DisplayName'] in SYSTEM_FOLDERS_NAMES else 'USER',  # TODO: Correct values?
        'parent_id': data['ParentFolderId'],  # TODO: remote_id or our db id?
    })

    return label
