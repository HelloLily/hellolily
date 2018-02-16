from email_wrapper_lib.models import EmailFolder


def parse_folder_list(data, promise=None):
    folder_list = [folder['id'] for folder in data.get('labels', [])]

    if promise:
        promise.resolve(folder_list)

    return folder_list


def parse_folder(data, promise=None):
    folder = {
        'remote_id': data['id'],
        # 'name': data['name'].split('/')[-1:],  # TODO: while we don't have parent_ids, use the name with slashes.
        'name': data['name'],
        'remote_value': data['name'],
        # 'message_count': data['messagesTotal'],
        'unread_count': data['messagesUnread'],
        'folder_type': EmailFolder.SYSTEM if data['type'] == 'system' else EmailFolder.USER,
        'parent_id': None,
    }

    if promise:
        promise.resolve(folder)

    return folder
