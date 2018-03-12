from collections import defaultdict


def parse_history(data, promise=None):

    # TODO: flatten the added_folders and deleted_folders into a list of updated_message_ids.

    history = {
        'page_token': None,  # The next page token, if there is one.
        'added_folders': defaultdict(list),  # Dict with message id as key and a list of label ids as value.
        'deleted_folders': defaultdict(list),  # Dict with message id as key and a list of label ids as value.

        # TODO: use sets, because _in_ operations are faster.
        'added_messages': [],  # List of message ids.
        'deleted_messages': [],  # List of message ids.
    }

    # Messages can be added, deleted and their folders chan be changed.
    # Every update on a message will show up as a seperate item in the history list.
    # That's why we first check for other updates, because there's a chance it cancels out.

    # For added messages the following is possible:
    #   The added message can be deleted again; this means we don't need to sync it.
    #   The added message can have changed folders; ignore the changed folders, because we need to sync from scratch.

    # For deleted messages the following is possible:
    #   Nothing, deletion is final.

    # For changed folders the following is possible:
    #   Folder changes can cancel eachother out: UNREAD is added -> UNREAD is removed -> nothing changed.

    if data:
        history_list = data.get('history', [])

        for history_item in history_list:
            for message in history_item.get('messagesAdded', []):
                remote_id = message['message']['id']

                if remote_id in history['added_folders']:
                    # Delete the added folders for this message, since it's new it has to be synced from scratch.
                    del history['added_folders'][remote_id]

                if remote_id in history['deleted_folders']:
                    # Delete the deleted folders for this message, since it's new it has to be synced from scratch.
                    del history['deleted_folders'][remote_id]

                history['added_messages'].append(remote_id)

            for message in history_item.get('messagesDeleted', []):
                remote_id = message['message']['id']

                if remote_id in history['added_messages']:
                    # Message was deleted before we ever synced it, not possible to sync it now.
                    history['added_messages'].remove(remote_id)

                if remote_id in history['added_folders']:
                    # Delete the added folders for this message, since it's deleted there's no need.
                    del history['added_folders'][remote_id]

                if remote_id in history['deleted_folders']:
                    # Delete the deleted folders for this message, since it's deleted there's no need.
                    del history['deleted_folders'][remote_id]

                history['deleted_messages'].append(remote_id)

            for change in history_item.get('labelsAdded', []):
                remote_id = change['message']['id']
                folder_ids = change['labelIds']

                if remote_id in history['added_messages'] or remote_id in history['deleted_messages']:
                    # If remote_id is in added or deleted messages -> do nothing.
                    continue

                if remote_id in history['deleted_folders']:
                    # There are deleted folders for this message, make sure we don't do double work.
                    # A new list is faster than removing items: https://stackoverflow.com/a/36268815/1310415.
                    deleted_f_ids = history['deleted_folders'][remote_id]
                    history['deleted_folders'][remote_id] = [f_id for f_id in deleted_f_ids if f_id not in folder_ids]

                history['added_folders'][remote_id] += folder_ids

            for change in history_item.get('labelsRemoved', []):
                remote_id = change['message']['id']
                folder_ids = change['labelIds']

                if remote_id in history['added_messages'] or remote_id in history['deleted_messages']:
                    # If remote_id is in added or deleted messages -> do nothing.
                    continue

                if remote_id in history['added_folders']:
                    # There are added folders for this message, make sure we don't do double work.
                    # A new list is faster than removing items: https://stackoverflow.com/a/36268815/1310415.
                    added_f_ids = history['added_folders'][remote_id]
                    history['added_folders'][remote_id] = [f_id for f_id in added_f_ids if f_id not in folder_ids]

                history['deleted_folders'][remote_id] += folder_ids

        history['page_token'] = data.get('nextPageToken')

    if promise:
        promise.resolve(history)

    return history
