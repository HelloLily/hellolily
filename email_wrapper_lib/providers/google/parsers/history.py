def parse_history(data, promise=None):
    history = {
        'page_token': None,
        'added_messages': [],
        'updated_messages': [],
        'deleted_messages': [],
    }

    if data:
        history_list = data.get('history', [])

        for history_item in history_list:
            for message in history_item.get('messagesAdded', []):
                remote_id = message['message']['id']
                history['added_messages'].append(remote_id)

            for message in history_item.get('messagesDeleted', []):
                remote_id = message['message']['id']

                if remote_id in history['added_messages']:
                    # Message was deleted before we ever synced it, not possible to sync it now.
                    history['added_messages'].remove(remote_id)

                if remote_id in history['updated_messages']:
                    # Delete the id from updated messages, since it's deleted there's no need.
                    del history['added_folders'][remote_id]

                history['deleted_messages'].append(remote_id)

            updated_messages = history_item.get('labelsAdded', []) + history_item.get('labelsRemoved', [])

            for message in updated_messages:
                remote_id = message['message']['id']

                if remote_id in history['added_messages'] or remote_id in history['deleted_messages']:
                    # If remote_id is in added or deleted messages -> do nothing.
                    continue

                history['updated_messages'].append(remote_id)

        history['page_token'] = data.get('nextPageToken')

    if promise:
        promise.resolve(history)

    return history
