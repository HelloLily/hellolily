from collections import defaultdict


def parse_history(data, promise=None):
    history_list = data.get('history', [])
    history = {
        'history_token': None,
        'page_token': None,
        'added_folders': defaultdict(list),
        'deleted_folders': defaultdict(list),
        'added_messages': [],
        'deleted_messages': [],
    }

    for history_item in history_list:
        for message in history_item.get('messagesAdded', []):
            history['added_messages'].append({
                'id': message.get('message').get('id'),
                'threadId': message.get('message').get('threadId')
            })

        for message in history_item.get('messagesDeleted', []):
            history['deleted_messages'].append(message.get('message').get('id'))

        # When users add and remove folders, it will show up as seperate items in the history.
        # That's why we first check if the user has done the opposite action, because it would cancel out.

        for change in history_item.get('labelsAdded', []):
            remote_id = change.get('message').get('id')
            folder_ids = change.get('labelIds')

            for folder in folder_ids:
                try:
                    history['deleted_folders'][remote_id].remove(folder)
                except ValueError:
                    history['added_folders'][remote_id].append(folder)

        for change in history_item.get('labelsRemoved', []):
            remote_id = change.get('message').get('id')
            folder_ids = change.get('labelIds')

            for folder in folder_ids:
                try:
                    history['added_folders'][remote_id].remove(folder)
                except ValueError:
                    history['deleted_folders'][remote_id].append(folder)

    history['history_token'] = data.get('historyId')
    history['page_token'] = data.get('nextPageToken')

    if promise:
        promise.resolve(history)

    return history
