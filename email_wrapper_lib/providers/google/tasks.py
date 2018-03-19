import logging

import operator
from celery import shared_task
from django.db.models import Q

from email_wrapper_lib.models import EmailAccount, EmailFolder, EmailMessageToEmailFolder, EmailMessage
from email_wrapper_lib.providers.google.builders import (
    save_new_messages, save_updated_messages, save_deleted_messages,
    save_new_folders, save_updated_folders, save_deleted_folders
)
from email_wrapper_lib.providers.google.connector import GoogleConnector
from email_wrapper_lib.providers.google.utils import new_batch
from email_wrapper_lib.tasks import LogErrorsTask


logger = logging.getLogger(__name__)


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def folder_sync(account_id):
    """
    Task to sync folders/labels from Google into our db.

    Sync strategy:
        - Get a list of all folder ids.
        - Calculate which folders are new, updated and deleted and handle them.

    Possible Errors:
        - Account could not be retrieved.
        - Folder ids could not be fetched.
        - Folders could not be saved to db.
    """
    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    # Create sets of the remote and database folders.
    api_folder_set = set(connector.folders.list())
    db_folder_set = set(account.folders.all().values_list('remote_id', flat=True))

    # Determine with set operations which folders to remove, create or update.
    create_folder_ids = api_folder_set - db_folder_set  # Folders that exist on remote but not in our db.
    update_folder_ids = api_folder_set & db_folder_set  # Folders that exist both on remote and in our db.
    delete_folder_ids = db_folder_set - api_folder_set  # Folders that exist in our db but not on remote.

    # TODO: check if this can be done async.
    if create_folder_ids:
        create_folders.apply(
            args=(account_id, create_folder_ids)
        )

    if update_folder_ids:
        update_folders.apply(
            args=(account_id, update_folder_ids)
        )

    if delete_folder_ids:
        delete_folders.apply(
            args=(account_id, delete_folder_ids)
        )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def create_folders(account_id, folder_ids):
    logger.info(
        'Started creating folders with args: account_id: {}, number of folders: {}'.format(
            account_id,
            len(folder_ids)
        )
    )

    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    # For every folder_id, get the details in a batch.
    batch = new_batch()
    folder_list = [connector.folders.get(folder_id, batch=batch) for folder_id in folder_ids]
    batch.execute()

    # Filter out empty promises.
    folder_list = [promise.data for promise in folder_list if promise.data]

    # Save the folders to db using the builder function.
    save_new_folders(account_id, folder_list)

    logger.info(
        'Finished creating folders with args: account_id: {}, number of folders: {}'.format(
            account_id,
            len(folder_ids)
        )
    )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def update_folders(account_id, folder_ids):
    logger.info(
        'Started updating folders with args: account_id: {}, number of folders: {}'.format(
            account_id,
            len(folder_ids)
        )
    )

    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    # For every folder_id, get the details in a batch.
    batch = new_batch()
    folder_list = [connector.folders.get(folder_id, batch=batch) for folder_id in folder_ids]
    batch.execute()

    # Filter out empty promises.
    folder_list = [promise.data for promise in folder_list if promise.data]

    # Save the folder updates to db using the builder function.
    save_updated_folders(account_id, folder_list)

    logger.info(
        'Finished updating folders with args: account_id: {}, number of folders: {}'.format(
            account_id,
            len(folder_ids)
        )
    )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def delete_folders(account_id, folder_ids):
    logger.info(
        'Started deleting folders with args: account_id: {}, number of folders: {}'.format(
            account_id,
            len(folder_ids)
        )
    )

    # Save the folder deletions to db using the builder function.
    save_deleted_folders(account_id, folder_ids)

    logger.info(
        'Finished deleting folders with args: account_id: {}, number of folders: {}'.format(
            account_id,
            len(folder_ids)
        )
    )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def list_sync(account_id, page_token):
    """
    Task to sync messages from Google into our db using the message list endpoint.

    Sync strategy:
        - Start at page 1; page_token = None.
        - Get a list of all message ids on the page.
        - Calculate which messages are new, updated and deleted and call the tasks to handle them.
        - If there's a next page, call this task to sync it.

    Possible errors:
        - Account could not be retrieved.
        - Message ids could not be fetched.
        - Message handling tasks could not be performed.
        - Account status could not be set to IDLE.
    """
    logger.info(
        'Started a list sync with args: account_id: {}, page_token: {}.'.format(
            account_id,
            page_token,
        )
    )

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
        # Create sets of the remote and database ids.
        api_message_set = set(message_list['messages'])
        db_message_set = set(
            account.messages.filter(remote_id__in=api_message_set).values_list('remote_id', flat=True)
        )

        # Determine with set operations which messages to remove and which to create or update.
        create_message_ids = api_message_set - db_message_set  # Messages that exist on remote but not in our db.
        update_message_ids = api_message_set & db_message_set  # Messages that exist both on remote and in our db.
        delete_message_ids = db_message_set - api_message_set  # Messages that exist in our db but not on remote.

        # TODO: check if this can be done async.
        if create_message_ids:
            create_messages.apply(
                args=(account_id, create_message_ids)
            )

        if update_message_ids:
            update_messages.apply(
                args=(account_id, update_message_ids)
            )

        if delete_message_ids:
            delete_messages.apply(
                args=(account_id, delete_message_ids)
            )

    # Check if this was the last page.
    if next_page_token:
        # Start a new task to sync the next page.
        list_sync.apply_async(
            kwargs={
                'account_id': account_id,
                'page_token': next_page_token,
            }
        )
        logger.info(
            'Starting another list sync from task with args: account_id: {}, page_token: {}.'.format(
                account_id,
                page_token,
            )
        )
    else:
        # stop syncing; set the status back to idle.
        EmailAccount.objects.filter(pk=account_id).update(status=EmailAccount.IDLE)
        logger.info(
            'Finished list sync. account_id: {}, page_token: {}.'.format(
                account_id,
                page_token,
            )
        )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def history_sync(account_id, history_id, page_token):
    """
    Task to sync messages from Google into our db using the history list endpoint.

    Sync strategy:
        - Start at page 1; page_token = None.
        - Get a summary of changes on the page, these already specify which messages are new, updated or deleted.
        - For every type of change, call the tasks to handle them.
        - If there's a next page, call this task to sync it.

    Possible errors:
        - Account could not be retrieved.
        - History could not be fetched.
        - Message handling tasks could not be performed.
        - Account status could not be set to IDLE.
    """
    logger.info(
        'Started history sync with args: account_id: {}, history_id: {}, page_token: {}.'.format(
            account_id,
            history_id,
            page_token,
        )
    )

    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    history_list = connector.history.list(history_id, page_token)
    next_page_token = history_list.get('next_page_token')

    # TODO: check if this can be done async.
    if history_list.get('added_messages'):
        create_messages.apply(
            args=(account_id, history_list.get('added_messages'))
        )

    if history_list.get('updated_messages'):
        update_messages.apply(
            args=(account_id, history_list.get('updated_messages'))
        )

    if history_list.get('deleted_messages'):
        delete_messages.apply(
            args=(account_id, history_list.get('deleted_messages'))
        )

    # Check if this was the last page.
    if next_page_token:
        # Start a new task to sync the next page.
        history_sync.apply_async(
            kwargs={
                'account_id': account_id,
                'history_id': history_id,
                'page_token': next_page_token,
            }
        )
        logger.info(
            'Started another history sync from task with args: account_id: {}, history_id: {}, page_token: {}.'.format(
                account_id,
                history_id,
                page_token,
            )
        )
    else:
        # stop syncing; set the status back to idle.
        EmailAccount.objects.filter(pk=account_id).update(status=EmailAccount.IDLE)
        logger.info(
            'Finished history sync with args: account_id: {}, history_id: {}, page_token: {}.'.format(
                account_id,
                history_id,
                page_token,
            )
        )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def create_messages(account_id, message_ids):
    logger.info(
        'Started creating messages with args: account_id: {}, number of messages: {}'.format(
            account_id,
            len(message_ids)
        )
    )

    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    # For every message_id, get the details (excluding body) in a batch.
    batch = new_batch()
    message_list = [connector.messages.minimal(msg_id, batch=batch) for msg_id in message_ids]
    batch.execute()

    # Filter out empty promises.
    # There is a bug between gmail/apple that creates empty messages.
    # More info: https://productforums.google.com/forum/#!topic/gmail/WyTczFXSjh0
    message_list = [msg_promise.data for msg_promise in message_list if msg_promise.data]

    # Save the messages to db using the builder function.
    save_new_messages(account_id, message_list)

    logger.info(
        'Finished creating messages with args: account_id: {}, number of messages: {}'.format(
            account_id,
            len(message_ids)
        )
    )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def update_messages(account_id, message_ids):
    logger.info(
        'Started updating messages with args: account_id: {}, number of messages: {}'.format(
            account_id,
            len(message_ids)
        )
    )

    try:
        account = EmailAccount.objects.get(pk=account_id)
    except EmailAccount.DoesNotExist:
        logger.info('Account matching query id={} does not exist.'.format(account_id))
        return

    connector = GoogleConnector(account.credentials, account.user_id)

    # For every message_id, get the folders in a batch.
    # The only thing that can be updated on a message are it's folders.
    batch = new_batch()
    message_list = [connector.messages.folders(msg_id, batch=batch) for msg_id in message_ids]
    batch.execute()

    # Filter out empty promises.
    # There is a bug between gmail/apple that creates empty messages.
    # More info: https://productforums.google.com/forum/#!topic/gmail/WyTczFXSjh0
    message_list = [msg_promise.data for msg_promise in message_list if msg_promise.data]

    # Save the message updates to db using the builder function.
    save_updated_messages(account_id, message_list)

    logger.info(
        'Finished updating messages with args: account_id: {}, number of messages: {}'.format(
            account_id,
            len(message_ids)
        )
    )


@shared_task(base=LogErrorsTask, trail=False, ignore_result=True)
def delete_messages(account_id, message_ids):
    logger.info(
        'Started deleting messages with args: account_id: {}, number of messages: {}'.format(
            account_id,
            len(message_ids)
        )
    )

    # Save the message deletions to db using the builder function.
    save_deleted_messages(account_id, message_ids)

    logger.info(
        'Finished deleting messages with args: account_id: {}, number of messages: {}'.format(
            account_id,
            len(message_ids)
        )
    )
