import urlparse

from email_wrapper_lib.providers.exceptions import BatchRequestException
from microsoft_mail_client.constants import SYSTEM_FOLDERS_NAMES


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


def parse_message_list(data, messages, message_resource):
    data = data.json()
    return messages


def parse_message(data, message):
    """
    A message that changes from folder, gets a new ID, but InternetMessageId stays with every mutation the same.
    ParentFolderId can tell if it is archived, trashed, or spam.
    """
    # Retrieve dict with 3 key, value pairs to map folders from remote_id to Archive, Trash and Junk.
    # result = EmailFolder.objects.filter()  # TODO: implement right query.
    # TODO: implement mapping ParentFolderId: DisplayName label
    folders = {'xyz': 'Junk Email', 'uvw': 'Archive', 'abc': 'Deleted Items'}

    data = data.json()
    message.update({
        'remote_id': data['InternetMessageId'],  # Don't use data['Id'], because it changes with folder mutations.
        'thread_id': data['ConversationId'],
        'history_token': '',  # TODO: Needed?
        'folder_ids': [data['ParentFolderId']],
        'snippet': data['BodyPreview'],
        'is_read': data['IsRead'],
        'is_starred': False,  # TODO: maybe 'pinned' messages? But available via API?
        'is_draft': data['IsDraft'],
        'is_important': data['Importance'] is 'High',
        'is_archived': data['ParentFolderId'] in folders and folders[data['ParentFolderId']] is 'Archive',
        'is_trashed': data['ParentFolderId'] in folders and folders[data['ParentFolderId']] is 'Deleted Items',
        'is_spam': data['ParentFolderId'] in folders and folders[data['ParentFolderId']] is 'Junk Email',
        'is_chat': False,
    })

    return message


def parse_label_list(data, labels, label_resource):
    data = data.json()
    """
    {u'@odata.context': u"https://outlook.office.com/api/v2.0/$metadata#Users('a%40outlook.com')/MailFolders",
    u'value': [{u'@odata.id': u"https://outlook.office.com/api/v2.0/Users('00034001')/MailFolders('AQMkADAwATM0MDAA')",
    u'ChildFolderCount': 0,
    u'DisplayName': u'Archive',
    u'Id': u'AQMkADAwATM0MDAAMS0wM2Y5LWVkMzYtMDACLTAwCgAuAAAD-Gudm_S5tkO5xIN4NveiEQEACQ2NI6ATzEGeCYmilLYoVgAAAgFOAAAA',
    u'ParentFolderId': u'AQMkADAwATM0MDAAMS0wM2Y5LWVkMzYtM',
    u'TotalItemCount': 0,
    u'UnreadItemCount': 0}]}
    """
    for label in data.get('value', []):
        labels[label['Id']] = label

        if label['ChildFolderCount'] > 0:
            labels.append(label_resource.list(label_id=label['Id']))

    # Are the more pages with labels on the current level?
    if '@odata.nextLink' in data:
        # Extract paging parameter from next_link.
        next_link = data.get('@odata.nextLink')
        skip = urlparse.parse_qs(urlparse.urlparse(next_link).query).get('$skip')
        labels.append(label_resource.list(label_id='?', skip=skip))  # TODO: Determine current label id.

    # if not label_resource.batch.empty:
    label_resource.batch.execute()  # Retrieve child labels or next page of labels.

    return labels


def parse_label(data, label):
    data = data.json()
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

    label.update({
        'id': data['Id'],
        'name': data['DisplayName'],
        'remote_value': data['DisplayName'],
        'message_count': data['TotalItemCount'],
        'unread_count': data['UnreadItemCount'],
        'folder_type': 'SYSTEM' if data['DisplayName'] in SYSTEM_FOLDERS_NAMES else 'USER',
        'parent_id': data['ParentFolderId'],  # TODO: remote_id or our db id?
    })

    return label
