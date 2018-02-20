import time
from celery import shared_task

from email_wrapper_lib.models import EmailAccount, EmailFolder
from email_wrapper_lib.providers.google.builders import create_messages
from email_wrapper_lib.providers.google.connector import GoogleConnector
from email_wrapper_lib.providers.google.utils import new_batch


@shared_task(trail=False, ignore_result=True)
def folder_sync(account_id):
    # TODO: catch errors and handle them.

    account = EmailAccount.objects.prefetch_related('folders').get(pk=account_id)
    connector = GoogleConnector(account.credentials, account.user_id)

    # Create sets of the remote and database folders.
    api_folder_set = set(connector.folders.list())
    db_folder_set = set(folder.remote_id for folder in account.folders.all())

    # Determine with set operations which folders to remove, create or update.
    create_folder_ids = api_folder_set - db_folder_set  # Folders that exist on remote but not in our db.
    update_folder_ids = api_folder_set & db_folder_set  # Folders that exist both on remote and in our db.
    delete_folder_ids = db_folder_set - api_folder_set  # Folders that exist in our db but not on remote.

    batch = new_batch()
    folders_to_create = [connector.folders.get(folder_id, batch=batch) for folder_id in create_folder_ids]
    folders_to_update = {folder_id: connector.folders.get(folder_id, batch=batch) for folder_id in update_folder_ids}
    batch.execute()

    EmailFolder.objects.bulk_create([EmailFolder(account=account, **folder.data) for folder in folders_to_create])

    if update_folder_ids:
        db_folders = account.folders.all()
        db_folders_by_remote_id = {folder.remote_id: folder for folder in db_folders}

        for folder_id in update_folder_ids:
            remote_folder = folders_to_update[folder_id].data
            db_folder = db_folders_by_remote_id[folder_id]

            check_attrs = ['remote_value', 'unread_count', 'parent_id', ]
            if any([getattr(db_folder, attr_name) != remote_folder.get(attr_name) for attr_name in check_attrs]):
                # There was an actual change to the folder, so we need to update it.
                db_folder.remote_value = remote_folder['remote_value']
                db_folder.name = remote_folder['name']
                db_folder.unread_count = remote_folder['unread_count']
                db_folder.parent_id = remote_folder['parent_id']

                db_folder.save(update_fields=['remote_value', 'name', 'unread_count', 'parent_id', ])

    if delete_folder_ids:
        EmailFolder.objects.filter(
            account=account,
            remote_id__in=delete_folder_ids
        ).delete()


@shared_task(trail=False, ignore_result=True)
def list_sync(account_id, page_token=None):
    start_time = time.time()
    print ''
    print ''

    setup_start_time = time.time()
    # TODO: only get values for account?
    account = EmailAccount.objects.get(pk=account_id)
    connector = GoogleConnector(account.credentials, account.user_id)

    message_list = connector.messages.list(page_token)
    print 'Setup time: {}'.format(time.time() - setup_start_time)

    # Google can return an empty page as last page, so check the results before doing any queries.
    if message_list:
        set_operations_start_time = time.time()
        # Create sets of the remote and database labels.
        api_message_set = set(message_list['messages'])
        # TODO: check all the queries that are being used.
        db_message_set = set(account.messages.all().values_list('remote_id', flat=True))

        # Determine with set operations which messages to remove and which to create or update.
        create_message_ids = api_message_set - db_message_set  # Messages that exist on remote but not in our db.
        update_message_ids = api_message_set & db_message_set  # Messages that exist both on remote and in our db.
        delete_message_ids = db_message_set - api_message_set  # Messages that exist in our db but not on remote.
        print 'Set operations time: {}'.format(time.time() - set_operations_start_time)

        batch_start_time = time.time()
        batch = new_batch()
        messages_to_create = [connector.messages.get(msg_id, batch=batch) for msg_id in create_message_ids]
        messages_to_update = {msg_id: connector.messages.get(msg_id, batch=batch) for msg_id in update_message_ids}
        batch.execute()
        print 'Batch time: {}'.format(time.time() - batch_start_time)

        create_messages_start_time = time.time()
        create_messages(account, messages_to_create)
        print 'Create messages time: {}'.format(time.time() - create_messages_start_time)
        # update_messages()
        # delete_messages()

    # Check if this was the last page, which it is when there is not next_page_token.
    if message_list.get('next_page_token'):
        list_sync.delay(
            account_id=account_id,
            page_token=message_list['next_page_token']
        )
    else:
        # stop syncing.
        EmailAccount.objects.filter(pk=account_id).update(status=EmailAccount.IDLE)
        print 'Done syncing account! {}'.format(account.username)

    print 'Total time in task: {}'.format(time.time() - start_time)




    # created_messages = []
    # if create_message_ids:
    #     created_messages = self.create_messages([api_messages[message_id] for message_id in create_message_ids])
    #
    # updated_messages = []
    # if update_message_ids:
    #     updated_messages = self.update_messages({
    #         remote_id: api_messages[remote_id] for remote_id in update_message_ids
    #     }, db_messages)
    #
    # if delete_message_ids:
    #     self.delete_messages(delete_message_ids)
    #
    # return created_messages + updated_messages



    # Sync strategy:

    # Get a list of all messages on the page.
        # IF fail
            # Fetch individual messages
                # IF fail
                    # Save an error object to the database to be displayed to the user
            # Save individual messages to db
                # IF fail
                    # Save an error object to the database to be displayed to the user
        # IF success
            # Save messages to db in bulk
                # IF fail
                    # Save individual messages to db
                        # IF fail
                            # Save an error object to the database to be displayed to the user


    # Possible errors
    # Account could not be retreived from db
    # Batch
        # Request error
        # Parsing error
        # DB save error
    # single
        # Request error
        # Parsing error
        # DB save error


@shared_task(trail=False, ignore_result=True)
def history_sync(account_id, page_token=None):
    pass
