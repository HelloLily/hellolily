from celery import chain, chord, group

from email_wrapper_lib.manager import Manager
from email_wrapper_lib.models import EmailAccount
from email_wrapper_lib.providers.google.connector import GoogleConnector
from email_wrapper_lib.providers.google.models import GoogleSyncInfo
from email_wrapper_lib.providers.google.tasks import stop_syncing, save_folders, save_page, debug_task, raising_task, \
    sync_error


class GoogleManager(Manager):
    def __init__(self, *args, **kwargs):
        super(GoogleManager, self).__init__(*args, **kwargs)

        self.connector = GoogleConnector(self.account.credentials, self.account.user_id)

        try:
            self.sync_info = self.account.google_sync_info
        except GoogleSyncInfo.DoesNotExist:
            self.sync_info = GoogleSyncInfo.objects.create(account=self.account)

    def sync(self, *args, **kargs):
        # TODO: check if it's a first sync or a partial sync and act accordingly.
        # TODO: for now we just implement the initial sync.
        self.account.status = EmailAccount.SYNCING
        self.account.save(update_fields=['status', ])

        # Save the current history id for this round of syncing.
        current_history_id = self.sync_info.history_id

        # Update the db to the new history id now, because there could be new messages between now and this sync.
        profile = self.connector.profile.get()
        self.sync_info.history_id = profile['history_id']
        self.sync_info.save(update_fields=['history_id', ])

        # Get a list of all pages to sync.
        pages = self.connector.messages.pages()
        # Step 1 is a single task that is  executed first.
        step_1 = save_folders.si(self.account.pk)
        # Step 2 is a group of tasks that are executed simultaneously, after step 1 is finished.
        # step_2 = [save_page.si(self.account.pk, page, current_history_id) for page in pages]
        step_2 = [debug_task.si('step_2', page_token=page) for page in pages]
        # step_2.append(raising_task.si('this is an error'))
        # Step 3 is a single task that is called after all the tasks in step 2 are finished.
        # step_3 = stop_syncing.si(self.account.pk)
        step_3 = debug_task.si('step_3')
        # Construct the chain and chord, so we can execute the tasks in the right order.
        steps = chain(step_1, group(step_2), step_3)
        # Start executing the tasks.
        result = steps()

        if self.blocking:
            # Wait for the result to be filled.
            return result.get()
        else:
            # Just return the result object unfilled.
            return result

    def sync_folders(self, *args, **kwargs):
        pass
