# from celery import shared_task
#
# from email_wrapper_lib.manager import EmailAccountManager
# from email_wrapper_lib.models.models import EmailAccount, EmailFolder
# from email_wrapper_lib.providers import Google, Microsoft
#
#
# @shared_task
# def sync_scheduler():
#     # TODO: filter(is_authorized=True, is_deleted=False): ?
#     for email_account_id in EmailAccount.objects.all().values_list('id', flat=True):
#         sync_account.delay(email_account_id)
#
#
# @shared_task
# def sync_account(account_id):
#     account = EmailAccount.objects.get(pk=account_id)
#
#     if account.status in [EmailAccount.SYNCING, EmailAccount.ERROR]:
#         # TODO: move to sync_scheduler() filter.
#         return
#
#     manager = EmailAccountManager(account)
#     manager.sync_folders()
#
#     # Google history.list end point synchronizes over 'all' mail where MS has a history for each folder. Google and MS
#     # message.list end point retrieves the messages for all folders. So in that case of a history sync, differentiate
#     # between Google and MS.
#     if account.provider_id == Google.id or account.status in [EmailAccount.NEW, EmailAccount.RESYNC]:
#         sync_messages.delay(account_id)
#     elif account.provider_id == Microsoft.id:
#         folder_ids = EmailFolder.objects.filter(account=account).values_list('id', flat=True)
#         for folder_id in folder_ids:
#             sync_messages_by_folder.delay(account_id, folder_id)
#
#
# @shared_task
# def sync_messages(account_id):
#     account = EmailAccount.objects.get(pk=account_id)
#     manager = EmailAccountManager(account)
#
#     manager.sync_messages()
#
#     # TODO: No need to reload account / retrieve updated data from db?
#     if account.page_token:
#         # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
#         sync_messages.delay(account_id)
#
#
# @shared_task
# def sync_messages_by_folder(account_id, folder_id):
#     account = EmailAccount.objects.get(pk=account_id)
#     folder = EmailFolder.objects.get(pk=folder_id)
#     manager = EmailAccountManager(account, folder)
#
#     manager.sync_messages_by_folder()
#
#     # TODO: No need to reload folder / retrieve updated data from db?
#     if folder.page_token:
#         # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
#         sync_messages_by_folder.delay(account_id, folder_id)
#
