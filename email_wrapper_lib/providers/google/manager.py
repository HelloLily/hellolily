from email_wrapper_lib.manager import Manager


class GoogleManager(Manager):
    def sync(self, *args, **kargs):
        # This is the main sync function.

        # Save history id for account.
        # Get/sync all labels for account.
            # OPTIONAL: do this in a task.
            # Use builder to save labels.
        # Get all page tokens for account message list.
        # Construct a celery chord to sync all page tokens and set the account.status afterward.
        pass

    def get_labels(self, *args, **kwargs):
        pass
