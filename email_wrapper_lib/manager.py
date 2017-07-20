from email_wrapper_lib.providers import registry


class EmailAccountManager(object):
    def __init__(self, account):
        self.account = account

        self.provider = registry[account.provider_id]
        self.connector = self.provider.connector(account.credentials, account.user_id)

    def add_labels_to_message(self, remote_id, label_ids):
        print ''
        print remote_id
        print label_ids
        print ''

    def remove_labels_from_message(self, remote_id, label_ids):
        print ''
        print remote_id
        print label_ids
        print ''

    def create_messages(self, messages):
        print ''
        print messages
        print ''

    def delete_messages(self, messages):
        print ''
        print messages
        print ''

    def sync_list(self):
        messages = self.connector.messages.list(self.account.page_token)
        self.connector.execute()

        self.create_messages(messages.get('messages'))

        if not self.account.history_token:
            self.account.history_token = messages.get('history_token')

        self.account.page_token = messages.get('page_token')

        self.account.save(updated_fields=['history_token', 'page_token'])

    def sync_history(self):
        changes = self.connector.history.list(self.account.history_token, self.account.page_token)
        self.connector.execute()

        for remote_id, labels in changes.get('added_labels').items():
            self.add_labels_to_message(remote_id, labels)

        for remote_id, labels in changes.get('deleted_labels').items():
            self.remove_labels_from_message(remote_id, labels)

        self.create_messages(changes.get('added_messages'))
        self.delete_messages(changes.get('deleted_messages'))

        self.account.page_token = changes.get('page_token')

        if not self.account.page_token:
            # Only override the history id after all pages are done.
            self.account.history_token = changes.get('history_token')

        self.account.save(updated_fields=['history_token', 'page_token'])
