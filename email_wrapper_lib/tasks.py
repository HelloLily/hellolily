from celery import shared_task

from email_wrapper_lib.manager import EmailAccountManager
from .models import EmailAccount


@shared_task
def sync_scheduler():
    for account in EmailAccount.objects.filter(is_active=True, is_syncing=False):
        sync.delay(account.pk)


@shared_task
def sync(account_id):
    account = EmailAccount.objects.get(pk=account_id)
    if account.is_syncing:
        return

    manager = EmailAccountManager(account)
    # TODO: sync labels, then sync messages.
    manager.sync_history()

    if account.page_token:
        # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
        sync.delay(account_id)


@shared_task
def first_sync(account_id):
    account = EmailAccount.objects.get(pk=account_id)
    if account.is_syncing:
        return

    manager = EmailAccountManager(account)
    # TODO: sync labels, then sync messages.
    manager.sync_list()

    if account.page_token:
        # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
        sync.delay(account_id)
