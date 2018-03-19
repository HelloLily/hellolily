from celery import chain

from email_wrapper_lib.manager import Manager
from email_wrapper_lib.models import EmailAccount
from email_wrapper_lib.providers.exceptions import ErrorStatusException, UnexpectedSyncStatusException
from email_wrapper_lib.providers.google.connector import GoogleConnector
from email_wrapper_lib.providers.google.models import GoogleSyncInfo
from email_wrapper_lib.providers.google.tasks import folder_sync, list_sync, history_sync


class GoogleManager(Manager):
    def __init__(self, *args, **kwargs):
        super(GoogleManager, self).__init__(*args, **kwargs)

        self.connector = GoogleConnector(self.account.credentials, self.account.user_id)

        try:
            self.sync_info = self.account.google_sync_info
        except GoogleSyncInfo.DoesNotExist:
            self.sync_info = GoogleSyncInfo.objects.create(account=self.account)

    def sync(self, *args, **kargs):
        if self.account.status in [EmailAccount.SYNCING, ]:
            # Don't sync an account twice.
            return
        elif self.account.status in [EmailAccount.ERROR, ]:
            raise ErrorStatusException('Email account is in error state and cannot be synced: {}-{}'.format(
                self.account.pk,
                self.account.user_id,
            ))
        elif self.account.status in [EmailAccount.NEW, EmailAccount.RESYNC, ]:
            # Sync using the messages list, loop over all messages.
            sync_task_signature = list_sync.si(
                account_id=self.account.pk,
                page_token=None
            )
        elif self.account.status in [EmailAccount.IDLE, ]:
            # Sync using the history list, getting only changes since last sync.
            sync_task_signature = history_sync.si(
                account_id=self.account.pk,
                history_id=self.sync_info.history_id,
                page_token=None
            )
        else:
            # This should never happen, the email account has a status that is unexpected.
            raise UnexpectedSyncStatusException('Unexpected sync status encountered for email account: {}-{}.'.format(
                self.account.pk,
                self.account.user_id,
            ))

        profile = self.connector.profile.get()

        # Set the account status to syncing, so we can start running tasks.
        self.account.status = EmailAccount.SYNCING
        self.account.messages_count = profile['messages_count']
        self.account.threads_count = profile['threads_count']
        self.account.save(update_fields=['status', 'messages_count', 'threads_count', ])

        # Update the db to the new history id now, because there could be new messages between now and this sync.
        self.sync_info.history_id = profile['history_id']
        self.sync_info.save(update_fields=['history_id', ])

        # Construct a chain of tasks to sync folders and after that start with the message sync.
        task_chain = chain(folder_sync.si(self.account.pk), sync_task_signature)

        # Start executing the tasks.
        task_chain.delay()

    def sync_folders(self, *args, **kwargs):
        pass
