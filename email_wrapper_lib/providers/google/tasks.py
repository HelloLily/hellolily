import logging

import operator
from celery import shared_task
from django.db.models import Q

from email_wrapper_lib.models import EmailAccount, EmailFolder, EmailMessageToEmailFolder, EmailMessage
from email_wrapper_lib.providers.google.builders import create_messages
from email_wrapper_lib.providers.google.connector import GoogleConnector
from email_wrapper_lib.providers.google.utils import new_batch
from email_wrapper_lib.tasks import LogErrorsTask


logger = logging.getLogger(__name__)


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
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


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def list_sync(account_id, page_token):
    logger.info('Started list sync. account_id: {}, page_token: {}.'.format(
        account_id,
        page_token,
    ))

    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    message_list = connector.messages.list(page_token)
    next_page_token = message_list.get('next_page_token')

    # Google can return an empty page as last page, so check the results before doing any queries.
    if message_list:
        # Create sets of the remote and database labels.
        api_message_set = set(message_list['messages'])
        db_message_set = set(account.messages.all().values_list('remote_id', flat=True))

        # Determine with set operations which messages to remove and which to create or update.
        create_message_ids = api_message_set - db_message_set  # Messages that exist on remote but not in our db.
        update_message_ids = api_message_set & db_message_set  # Messages that exist both on remote and in our db.
        delete_message_ids = db_message_set - api_message_set  # Messages that exist in our db but not on remote.

        # Create a new batch request to get the details of the messages needed.
        batch = new_batch()
        messages_to_create = [connector.messages.get(msg_id, batch=batch) for msg_id in create_message_ids]
        messages_to_update = {msg_id: connector.messages.get(msg_id, batch=batch) for msg_id in update_message_ids}
        batch.execute()

        create_messages(account, messages_to_create)

        # update_messages()
        # delete_messages()

    # Check if this was the last page.
    if next_page_token:
        # Start a new task to sync the next page.
        list_sync.delay(
            account_id=account_id,
            page_token=next_page_token
        )
    else:
        # stop syncing; set the status back to idle.
        EmailAccount.objects.filter(pk=account_id).update(status=EmailAccount.IDLE)
        logger.info('Done syncing the list for account {}'.format(account.pk))

        logger.info('Finished list sync. account_id: {}, page_token: {}.'.format(
            account_id,
            page_token,
        ))

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
    # Start at page 1; page_token = None
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


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def history_sync(account_id, history_id, page_token):
    logger.info('Started history sync. account_id: {}, history_id: {}, page_token: {}.'.format(
        account_id,
        history_id,
        page_token,
    ))

    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    history_list = connector.history.list(history_id, page_token)
    next_page_token = history_list.get('next_page_token')

    folder_dict = {
        f[0]: f[1] for f in EmailFolder.objects.filter(account_id=account_id).values_list('remote_id', 'id')
    }
    message_dict = {
        m[0]: m[1] for m in EmailMessage.objects.filter(account_id=account_id).values_list('remote_id', 'id')
    }

    folders_to_create = []
    for message_id, folders in history_list.get('added_folders', {}).items():
        for folder_id in folders:
            folders_to_create.append(
                EmailMessageToEmailFolder(
                    emailmessage_id=message_dict[message_id],
                    emailfolder_id=folder_dict[folder_id]
                )
            )

    folders_to_delete = []
    for message_id, folders in history_list.get('deleted_folders', {}).items():
        query = reduce(operator.or_, (
            Q(
                emailmessage_id=message_dict[message_id],
                emailfolder_id=folder_dict[folder_id]
            ) for folder_id in folders
        ))
        folders_to_delete.append(query)

    batch = new_batch()
    messages_to_create = [connector.messages.get(msg_id, batch=batch) for msg_id in history_list.get('added_messages')]
    batch.execute()

    create_messages(account, messages_to_create)

    EmailMessageToEmailFolder.objects.bulk_create(folders_to_create)

    if folders_to_delete:
        folders_to_delete = reduce(operator.or_, folders_to_delete)
        EmailMessageToEmailFolder.objects.filter(folders_to_delete).delete()

    EmailMessage.objects.filter(remote_id__in=history_list.get('deleted_messages'))

    # Check if this was the last page.
    if next_page_token:
        # Start a new task to sync the next page.
        history_sync.delay(
            account_id=account_id,
            history_id=history_id,
            page_token=next_page_token
        )
    else:
        # stop syncing; set the status back to idle.
        EmailAccount.objects.filter(pk=account_id).update(status=EmailAccount.IDLE)
        logger.info('Finished history sync. account_id: {}, history_id: {}, page_token: {}.'.format(
            account_id,
            history_id,
            page_token,
        ))


# TODO: find out if the above tasks can call these tasks async.
# TODO: only on the last page should it not be async, so the account syncing status can be set to IDLE afterwards.


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def create_messages(account_id, message_ids):
    pass


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def update_messages(account_id, message_ids):
    # TODO: for list_sync we only have remote_ids and for history_sync we have added and removed labels.
    # TODO: if we can find a way to efficiently determine what operations need to be done after fetching the labels
    # TODO: we can combine the two operations in a generic update_messages function/task.

    # TODO: new way to only get the labels for a remote_id.
    # TODO: set is_read and stuff according to new labels.
    # TODO: update message in db

    pass


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def delete_messages(account_id, message_ids):
    pass
