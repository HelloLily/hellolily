from celery import shared_task

from email_wrapper_lib.models import EmailAccount, EmailFolder
from email_wrapper_lib.providers.google.connector import GoogleConnector


@shared_task
def debug_task(name, *args, **kwargs):
    print ''
    print ''
    print 'DEBUG[{}]: {}'.format(name, args)
    print 'DEBUG[{}]: {}'.format(name, kwargs)
    print ''
    print ''


@shared_task
def raising_task(msg):
    raise ValueError(msg)


@shared_task
def sync_error(request, exc, traceback):
    print 'there was a sync error which we can handle.'


@shared_task
def save_folders(account_id):
    # TODO: catch errors and handle them.

    account = EmailAccount.objects.prefetch_related('folders').get(pk=account_id)
    connector = GoogleConnector(account.credentials, account.user_id)

    folders = connector.folders.list()

    # Create sets of the remote and database folders.
    api_folder_set = set(folders)
    db_folder_set = set(folder.remote_id for folder in account.folders.all())

    # Determine with set operations which folders to remove, create or update.
    create_folder_ids = api_folder_set - db_folder_set  # Folders that exist on remote but not in our db.
    update_folder_ids = api_folder_set & db_folder_set  # Folders that exist both on remote and in our db.
    delete_folder_ids = db_folder_set - api_folder_set  # Folders that exist in our db but not on remote.

    print 'Folders to create:'
    print create_folder_ids
    print ''

    print 'Folders to update:'
    print update_folder_ids
    print ''

    print 'Folders to delete:'
    print delete_folder_ids
    print ''

    # if create_folder_ids:
    #     bulk = []
    #     for folder_id in create_folder_ids:
    #         folder = folders[folder_id]
    #         # TODO: the parser should set the folder type according to the model integer choices.
    #
    #         bulk.append(EmailFolder(
    #             account=account,
    #             **folder
    #         ))
    #     EmailFolder.objects.bulk_create(bulk)
    #
    # if update_folder_ids:
    #     db_folders = account.folders
    #     db_folders_by_remote_id = {folder.remote_id: folder for folder in db_folders}
    #
    #     for folder_id in update_folder_ids:
    #         remote_folder = folders[folder_id]
    #         db_folder = db_folders_by_remote_id[folder_id]
    #
    #         check_attrs = ['remote_value', 'unread_count', 'parent_id', ]
    #         if any([getattr(db_folder, attr_name) != getattr(remote_folder, attr_name) for attr_name in check_attrs]):
    #             # There was an actual change to the folder, so we need to update it.
    #             db_folder.remote_value = remote_folder.remote_value
    #             db_folder.name = remote_folder.name
    #             db_folder.unread_count = remote_folder.unread_count
    #             db_folder.parent_id = remote_folder.parent_id
    #
    #             db_folder.save(update_fields=['remote_value', 'name', 'unread_count', 'parent_id', ])
    #
    # if delete_folder_ids:
    #     EmailFolder.objects.filter(
    #         account=account,
    #         remote_id__in=delete_folder_ids
    #     ).delete()


@shared_task
def save_page(account_id, page_token):
    account = EmailAccount.objects.get(pk=account_id)
    connector = GoogleConnector(account.credentials, account.user_id)

    messages = connector.messages.list(page_token)

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

    for message in messages:
        # TODO: save pages of messages
        pass


@shared_task
def stop_syncing(account_id):
    account = EmailAccount.objects.get(pk=account_id)

    account.status = EmailAccount.IDLE
    account.save(update_fields=['status', ])
