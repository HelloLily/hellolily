from celery import shared_task

from email_wrapper_lib.manager import EmailAccountManager
from email_wrapper_lib.models.models import EmailAccount, EmailFolder
from email_wrapper_lib.providers import Google, Microsoft


@shared_task
def sync_scheduler():
    for email_account_id in EmailAccount.objects.all().values_list('id', flat=True):  # TODO: filter(is_authorized=True, is_deleted=False): ?
        sync_account.delay(email_account_id)


@shared_task
def sync_account(account_id):
    account = EmailAccount.objects.get(pk=account_id)

    if account.status in [EmailAccount.SYNCING, EmailAccount.ERROR]:
        # TODO: move to sync_scheduler() filter.
        return

    manager = EmailAccountManager(account)
    manager.sync_folders()

    if account.provider_id == Google.id:
        sync_messages.delay(account_id)
    elif account.provider_id == Microsoft.id:
        if account.status in [EmailAccount.NEW, EmailAccount.RESYNC]:
            sync_messages.delay(account_id)
        else:
            folder_ids = EmailFolder.objects.filter(account=account).values_list('id', flat=True)
            for folder_id in folder_ids:
                sync_messages_by_folder.delay(account_id, folder_id)


@shared_task
def sync_messages(account_id):
    account = EmailAccount.objects.get(pk=account_id)
    manager = EmailAccountManager(account)

    manager.sync_messages()

    # TODO: No need to reload account / retrieve updated data from db?
    if account.page_token:
        # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
        sync_messages.delay(account_id)


@shared_task
def sync_messages_by_folder(account_id, folder_id):
    account = EmailAccount.objects.get(pk=account_id)
    folder = EmailFolder.objects.get(pk=folder_id)
    manager = EmailAccountManager(account, folder)

    manager.sync_messages_by_folder()

    # TODO: No need to reload folder / retrieve updated data from db?
    if folder.page_token:
        # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
        sync_messages_by_folder.delay(account_id, folder_id)


# @shared_task
# def sync_messages(account_id, folder_id=None):
#     account = EmailAccount.objects.get(pk=account_id)
#
#     manager = EmailAccountManager(account)
#
#     if account.provider_id == Google.id:
#         manager.sync_messages()
#
#         if account.page_token:
#             sync_messages.delay(account_id)
#
#     elif account.provider_id == Microsoft.id:
#         if not folder_id:
#             folders = EmailFolder.objects.filter(account=account)
#             for folder in folders:
#                 manager.sync_messages_ms.delay(folder.pk)
#         else:
#             manager.sync_messages_ms.delay(folder_id)
#
#         folders = EmailFolder.objects.filter(account=account_id).exclude(page_token__isnull=True).exclude(page_token='')
#         for folder in folders:
#             sync_messages.delay(folder.pk)


# @shared_task
# def first_sync(account_id):
#     account = EmailAccount.objects.get(pk=account_id)
#     if account.is_syncing:
#         return
#
#     manager = EmailAccountManager(account)
#     manager.sync_labels()
#     manager.sync_list()
#
#     if account.page_token:
#         # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
#         first_sync.delay(account_id)
