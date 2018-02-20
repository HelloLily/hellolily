from celery import chain, chord, group

from email_wrapper_lib.manager import Manager
from email_wrapper_lib.models import EmailAccount
from email_wrapper_lib.providers.google.connector import GoogleConnector
from email_wrapper_lib.providers.google.models import GoogleSyncInfo
from email_wrapper_lib.providers.google.tasks import folder_sync, list_sync


class GoogleManager(Manager):
    def __init__(self, *args, **kwargs):
        super(GoogleManager, self).__init__(*args, **kwargs)

        self.connector = GoogleConnector(self.account.credentials, self.account.user_id)

        try:
            self.sync_info = self.account.google_sync_info
        except GoogleSyncInfo.DoesNotExist:
            self.sync_info = GoogleSyncInfo.objects.create(account=self.account)

    def sync(self, *args, **kargs):
        # TODO: check if status = syncing => raise error. Don't sync an account twice at the same time.
        self.account.status = EmailAccount.SYNCING
        self.account.save(update_fields=['status', ])

        # Save the current history id for this round of syncing.
        current_history_id = self.sync_info.history_id

        # TODO: check if it's a first sync or a partial sync and act accordingly.
        # TODO: for now we just implement the initial sync.

        # Update the db to the new history id now, because there could be new messages between now and this sync.
        profile = self.connector.profile.get()
        self.sync_info.history_id = profile['history_id']
        self.sync_info.save(update_fields=['history_id', ])

        # Construct a chain of tasks to sync folders and after that start with the message list.
        task_chain = chain(
            folder_sync.si(self.account.pk),
            list_sync.si(self.account.pk)
        )

        # Start executing the tasks.
        task_chain.delay()

    def sync_folders(self, *args, **kwargs):
        pass
