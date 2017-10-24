from celery import shared_task

from email_wrapper_lib.manager import EmailAccountManager
from email_wrapper_lib.models.models import EmailAccount


@shared_task
def sync_scheduler():
    for account in EmailAccount.objects.all():
        sync_account.delay(account.pk)


@shared_task
def sync_account(account_id):
    account = EmailAccount.objects.get(pk=account_id)

    if account.status in [EmailAccount.SYNCING, EmailAccount.ERROR]:
        return

    manager = EmailAccountManager(account)
    manager.sync_folders()

    sync_messages.delay(account_id)


@shared_task
def sync_messages(account_id):
    account = EmailAccount.objects.get(pk=account_id)

    manager = EmailAccountManager(account)
    manager.sync_messages()

    if account.page_token:
        # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
        sync_messages.delay(account_id)


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
