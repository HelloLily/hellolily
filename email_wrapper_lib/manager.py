from collections import defaultdict

from django.db import transaction

from email_wrapper_lib.models.models import (
    EmailMessage, EmailFolder, EmailAccount, EmailMessageToEmailRecipient, EmailRecipient
)
from email_wrapper_lib.providers import registry


# manager = Manager(account=some_account)
# manager.sync()


class EmailFolderManager(object):
    def __init__(self):
        super(EmailFolderManager, self).__init__()

    def save(self):
        pass

    def create(self):
        pass

    def update(self):
        pass


class EmailMessageManager(object):
    def __init__(self):
        super(EmailMessageManager, self).__init__()

    def save(self):
        pass

    def create(self):
        pass

    def update(self):
        pass


class EmailAccountManager(object):
    _old_status = None

    def __init__(self, account):
        self.account = account

        self.provider = registry[account.provider_id]
        self.connector = self.provider.connector(account.user_id, account.credentials)

    def start(self):
        self._old_status = self.account.status
        self.account.status = EmailAccount.SYNCING
        self.account.save()

    def stop(self, updated_fields=('status', 'page_token', 'history_token')):
        if self.account.page_token:
            # If there is a page token, we continue with the sync so we put the old status back while idle.
            self.account.status = self._old_status
        elif self.account.status != EmailAccount.ERROR:
            # If the status is not error we put it to idle.
            self.account.status = EmailAccount.IDLE

        self.account.save(updated_fields=updated_fields)

    def sync_folders(self):
        self.start()

        folders = self.connector.labels.list()
        self.connector.execute()

        self.save_folders(folders)

        self.stop()

    def save_folders(self, folders, db_folders=None):
        if not db_folders:
            db_folders = EmailFolder.objects.filter(account_id=self.account.pk)

        # Create sets of the remote and database labels.
        api_folder_set = set(folders.keys())
        db_folder_set = set(label.remote_id for label in db_folders)

        # Determine with set operations which labels to remove and which to create or update.
        create_folder_ids = api_folder_set - db_folder_set  # Labels that exist on remote but not in our db.
        update_folder_ids = api_folder_set & db_folder_set  # Labels that exist both on remote and in our db.
        delete_folder_ids = db_folder_set - api_folder_set  # Labels that exist in our db but not on remote.

        if create_folder_ids:
            self.create_folders([folders[folder_id] for folder_id in create_folder_ids])

        if update_folder_ids:
            self.update_folders({folder_id: folders[folder_id] for folder_id in update_folder_ids}, db_folders)

        if delete_folder_ids:
            self.delete_folders(delete_folder_ids)

    def create_folders(self, folder_list):
        bulk = []
        for folder in folder_list:
            # TODO: set the folder type according to the model integer choices.

            bulk.append(EmailFolder(
                account=self.account,
                **folder
            ))
        return EmailFolder.objects.bulk_create(bulk)

    def update_folders(self, remote_folders, db_folders=None):
        if not db_folders:
            db_folders = EmailFolder.objects.filter(account_id=self.account.pk)

        db_folders_by_remote_id = {folder.remote_id: folder for folder in db_folders}

        for remote_id, remote_folder in enumerate(remote_folders):
            db_folder = db_folders_by_remote_id[remote_id]

            if (
                db_folder.remote_value != remote_folder.remote_value or
                db_folder.unread_count != remote_folder.unread_count or
                db_folder.parent_id != remote_folder.parent_id
            ):
                # There was an actual change to the folder, so we need to update it.
                db_folder.remote_value = remote_folder.remote_value
                db_folder.name = remote_folder.name
                db_folder.unread_count = remote_folder.unread_count
                db_folder.parent_id = remote_folder.parent_id

                db_folder.save(updated_fields=['remote_value', 'name', 'unread_count', 'parent_id'])

        # TODO: check if this contains the updated instances.
        return db_folders

    def delete_folders(self, remote_ids):
        EmailFolder.objects.filter(
            account=self.account,
            remote_id__in=remote_ids
        ).delete()

    def sync_messages(self):
        self.start()

        if self._old_status in [EmailAccount.NEW, EmailAccount.RESYNC]:
            # This is a new account or one that needs to resync.
            profile = self.connector.profile.get()
            data = self.connector.messages.list(self.account.page_token)
            self.connector.execute()

            self.save_list(data['messages'])

            if not self.account.history_token:
                # Only save the history token on first iteration.
                self.account.history_token = profile.get('history_token')

        else:
            # This is an existing account that can sync using the history id.
            data = self.connector.history.list(self.account.history_token, self.account.page_token)
            self.connector.execute()

            self.save_history(data)

            if not self.account.page_token:
                # Only override the history id after all pages are done.
                self.account.history_token = data.get('history_token')

        self.account.page_token = data.get('page_token')

        self.stop()

    def save_list(self, api_messages):
        # Create sets of the remote and database labels.
        api_message_set = set([message.get('remote_id') for message in api_messages])
        db_messages = EmailMessage.objects.filter(account_id=self.account.pk, remote_id__in=api_message_set)
        db_message_set = set(message.remote_id for message in db_messages)

        # Determine with set operations which messages to remove and which to create or update.
        create_message_ids = api_message_set - db_message_set  # Messages that exist on remote but not in our db.
        update_message_ids = api_message_set & db_message_set  # Messages that exist both on remote and in our db.
        delete_message_ids = db_message_set - api_message_set  # Messages that exist in our db but not on remote.

        created_messages = []
        if create_message_ids:
            created_messages = self.create_messages([api_messages[message_id] for message_id in create_message_ids])

        updated_messages = []
        if update_message_ids:
            updated_messages = self.update_messages({
                remote_id: api_messages[remote_id] for remote_id in update_message_ids
            }, db_messages)

        if delete_message_ids:
            self.delete_messages(delete_message_ids)

        return created_messages + updated_messages

    def save_history(self, history):
        # save messages to db according to history id.
        pass

    def save_recipients(self, recipients):
        recipients = {
            # 'remote_id': {
            #     'to': [recipient_obj, recipient_obj, ],
            #     'cc': [recipient_obj, ],
            #     'bcc': [recipient_obj, ],
            #     'from': [recipient_obj, recipient_obj, ],
            #     'sender': [recipient_obj],
            #     'reply_to': [recipient_obj],
            # }
        }

        api_raw_value_list = []
        # Loop over the recipients dict, first get the remote id and the message info (dict with to, from, cc, ...).
        for remote_id, recipient_dict in recipients.items():
            # Loop over the message info and extract the relation between the message and recipients in the list.
            for recipient_type_label, recipient_list in recipient_dict:
                api_raw_value_list += [recipient.get('raw_value') for recipient in recipient_list]

        api_recipient_set = set(api_raw_value_list)
        db_recipients = EmailRecipient.objects.filter(raw_value__in=api_recipient_set)

        db_raw_value_list = []
        db_recipient_dict = {}
        for recipient in db_recipients:
            db_raw_value_list.append(recipient.raw_value)
            db_recipient_dict[recipient.raw_value] = recipient

        db_recipient_set = set(db_raw_value_list)

        recipients_with_instances = {}
        recipients_to_be_created = []
        for remote_id, recipient_dict in recipients.items():
            recipients_with_instances[remote_id] = defaultdict(list)

            for recipient_type_label, recipient_list in recipient_dict:
                for recipient_data in recipient_list:
                    raw_value = recipient_data.get('raw_value')

                    if raw_value in api_recipient_set and raw_value in db_recipient_set:
                        recipient = db_recipient_dict[raw_value]
                    else:
                        recipient = EmailMessageToEmailRecipient(**recipient_data)
                        recipients_to_be_created.append(recipient)

                    recipients_with_instances[remote_id][recipient_type_label].append(recipient)

        EmailRecipient.objects.bulk_create(recipients_to_be_created)

        return recipients_with_instances

    def create_messages(self, message_list):
        messages = {
            # 'remote_id': 'message object',
        }
        recipients = {
            # 'remote_id': {
            #     'to': [recipient_obj, recipient_obj, ],
            #     'cc': [recipient_obj, ],
            #     'bcc': [recipient_obj, ],
            #     'from': [recipient_obj, recipient_obj, ],
            #     'sender': [recipient_obj],
            #     'reply_to': [recipient_obj],
            # }
        }

        # Loop through messages from remote.
        for message in message_list:
            # Add a message object under it's remote id to the messages list.
            messages.update({message.get('remote_id'): EmailMessage(account=self.account, **message)})

            # For all the recipient fields add the recipient data under the remote id to the recipients dict.
            type_dict = {}
            for recipient_type in ['to', 'cc', 'bcc', 'from', 'sender', 'reply_to']:
                type_dict[recipient_type] = message.get(recipient_type, [])
            recipients[message.get('remote_id')] = type_dict

        with transaction.atomic():
            # TODO: save folders for messages.
            # Bulk create the messages, populating the message objects with pks.
            created_messages = EmailMessage.objects.bulk_create(messages.values())
            # Bulk create/update the recipients, replacing the recipient data dicts with db objects.
            recipients = self.save_recipients(recipients)

            bulk = []
            # Loop over the recipients dict, first get the remote id and the message info (dict with to, from, cc, ..).
            for remote_id, recipient_dict in recipients.items():
                # Get the actual id of the db message object out of the messages list.
                message_id = messages[remote_id].pk

                # Loop over the message info and extract the relation between the message and recipients in the list.
                for recipient_type_label, recipient_list in recipient_dict:
                    # Convert the string value to an integer which can be saved in the db.
                    recipient_type = recipient_type_label  # TODO: get the int for this.

                    # Loop over all the recipient objects in the list, and create a message->recipient relation object.
                    for recipient_obj in recipient_list:
                        bulk.append(EmailMessageToEmailRecipient(
                            message_id=message_id,
                            recipient_id=recipient_obj.pk,
                            recipient_type=recipient_type
                        ))

            # Bulk create the relation between messages and recipients.
            EmailMessageToEmailRecipient.objects.bulk_create(bulk)

        return created_messages

    def update_messages(self, remote_messages, db_messages):
        db_message_dict = {msg.remote_id: msg for msg in db_messages}
        folders = {folder.remote_id: folder for folder in self.account.folders.all()}

        for msg in remote_messages:
            message = db_message_dict[msg.get('remote_id')]
            folders_for_message = []

            for folder_id in msg.get('folder_ids'):
                folders_for_message

            message.is_read = msg.get('is_read')
            message.save()

        return db_messages  # Because it's the same obj in memory this can just be returned.

    def delete_messages(self, remote_ids):
        EmailMessage.objects.filter(
            account=self.account,
            remote_id__in=remote_ids
        ).delete()

    # def add_labels_to_message(self, remote_id, data):
    #     pass
    #
    # def remove_labels_from_message(self, remote_id, data):
    #     # TODO: find all the labels and bulk delete them.
    #     pass
    #
    # def save_recipients(self, recipients):
    #     # TODO: get the existing recipients.
    #     # TODO: bulk create all EmailRecipient's. (those that don't exist yet)
    #     # TODO: get the existing roles.
    #     # TODO: bulk create all EmailMessageToEmailRecipient's. (those that don't exist yet)
    #
    #     pass
    #
    # def save_messages(self, messages):
    #     message_list = []
    #
    #     for remote_id, data in messages.items():
    #         data.update({
    #             'account_id': self.account.pk,
    #         })
    #
    #         message_list.append(EmailMessage(**data))
    #
    #     with transaction.atomic():
    #         EmailMessage.objects.bulk_create(*message_list)
    #
    #         for message in messages:
    #             self.add_labels_to_message(message.remote_id, message)
    #
    #         self.save_recipients(messages)
    #
    # def delete_messages(self, messages):
    #     print ''
    #     print messages
    #     print ''

    # def sync_list(self):
    #     profile = {}
    #     if not self.account.history_token:
    #         profile = self.connector.profile.get()
    #
    #     messages = self.connector.messages.list(self.account.page_token)
    #     self.connector.execute()
    #
    #     self.save_messages(messages.get('messages'))
    #
    #     self.account.page_token = messages.get('page_token')
    #     self.account.history_token = profile.get('history_token')
    #
    #     self.account.save(update_fields=['history_token', 'page_token'])
    #
    # def sync_history(self):
    #     changes = self.connector.history.list(self.account.history_token, self.account.page_token)
    #     self.connector.execute()
    #
    #     for remote_id, labels in changes.get('added_labels', {}).items():
    #         # TODO: do this inline, should be simple with the given label ids.
    #         self.add_labels_to_message(remote_id, labels)
    #
    #     for remote_id, labels in changes.get('deleted_labels', {}).items():
    #         # TODO: do this inline, should be simple with the given label ids.
    #         self.remove_labels_from_message(remote_id, labels)
    #
    #     self.save_messages(changes.get('added_messages'))
    #     self.delete_messages(changes.get('deleted_messages'))
    #
    #     self.account.page_token = changes.get('page_token')
    #
    #     if not self.account.page_token:
    #         # Only override the history id after all pages are done.
    #         self.account.history_token = changes.get('history_token')
    #
    #     self.account.save(update_fields=['history_token', 'page_token'])
