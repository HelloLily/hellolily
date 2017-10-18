import logging
import gc

from django.conf import settings
from googleapiclient.errors import HttpError

from lily.celery import app
from .builders.label import LabelBuilder
from .builders.message import MessageBuilder
from .connector import GmailConnector, NotFoundError, LabelNotFoundError, MailNotEnabledError
from .credentials import InvalidCredentialsError
from .models.models import EmailLabel, EmailMessage, NoEmailMessageId

logger = logging.getLogger(__name__)


class GmailManager(object):
    """
    Manager for handling in and output of EmailAccount that connects through Gmail Api.

    Attributes:
        connector: GmailConnector instance
        email_account: EmailAccount instance
        message_builder: MessageBuilder instance
        label_builder: LabelBuilder instance
    """
    def __init__(self, email_account):
        """
        Args:
            email_account (instance): EmailAccount instance
        """
        self.email_account = email_account
        try:
            self.connector = GmailConnector(self.email_account)
        except InvalidCredentialsError:
            logger.debug('Didn\'t initialize connector: invalid credentials for account %s' % email_account)
            raise
        else:
            self.message_builder = MessageBuilder(self)
            self.label_builder = LabelBuilder(self)

    def full_synchronize(self):
        message_ids = self.connector.get_all_message_id_list()

        # Check for message_ids that are saved as non email messages.
        no_message_ids_in_db = set(
            NoEmailMessageId.objects.filter(
                account=self.email_account
            ).values_list('message_id', flat='true')
        )

        # Check for message_ids that are saved as email messages.
        message_ids_in_db = set(
            EmailMessage.objects.filter(
                account=self.email_account
            ).values_list('message_id', flat='true')
        )

        # What do we need to do with every email message?
        for i, message_dict in enumerate(message_ids):
            logger.debug('Check for existing messages, %s/%s' % (i, len(message_ids)))
            if message_dict['id'] in no_message_ids_in_db:
                # Not an email, but chatmessage, skip.
                pass
            elif message_dict['id'] not in message_ids_in_db:
                # Message is new.
                app.send_task(
                    'download_email_message',
                    args=[self.email_account.id, message_dict['id']],
                    queue='email_first_sync'
                )
            else:
                # We only need to update the labels for this message.
                app.send_task(
                    'update_labels_for_message',
                    args=[self.email_account.id, message_dict['id']],
                    queue='email_first_sync'
                )

        # Finally, add a task to keep track when the sync queue is finished.
        app.send_task(
            'full_sync_finished',
            args=[self.email_account.id],
            queue='email_first_sync'
        )
        # Only if transaction was successful, we update the history ID.
        self.connector.save_history_id()
        logger.debug('Finished queuing up tasks for email sync, storing history id for %s' % self.email_account)

    def download_message(self, message_id):
        """
        Download message from Google and parse into an EmailMessage.

        Arguments:
            message_id (str): message_id of the message
        """
        # If message is already downloaded, only update it.
        if EmailMessage.objects.filter(account=self.email_account, message_id=message_id).order_by().exists():
            self.update_labels_for_message(message_id)
            return

        # Fetch the info from the connector and only store it if it is still out there.
        try:
            message_info = self.connector.get_message_info(message_id)
        except NotFoundError:
            logger.debug('Message already deleted from remote')
        else:
            # TODO: LILY-2203 draft_id is missing when downloaded message is a draft.
            self.message_builder.store_message_info(message_info, message_id)
            self.message_builder.save()

    def sync_by_history(self):
        """
        Synchronize EmailAccount by history.

        Fetches the changes from the GMail api and creates tasks for the mutations.
        """
        logger.info('updating history for %s with history_id %s' % (self.email_account, self.email_account.history_id))
        old_history_id = self.email_account.history_id

        try:
            history = self.connector.get_history()
        except MailNotEnabledError:
            self.email_account.is_authorized = False
            self.email_account.is_syncing = False
            self.email_account.save()
            logger.error('Mail not enabled for this account. Mail sync stopped for account %s' % self.email_account)
            return
        except NotFoundError:
            # A NotFoundError (http error code 404) is given when the suplied historyId is invalid.
            # Synchronization of email can be restored by initiating a full sync on the account. This is covered
            # in the synchronize_email_account_scheduler task by looking at the sync_failure_count.
            self.email_account.sync_failure_count += 1
            self.email_account.save()
            if self.email_account.sync_failure_count > settings.MAX_SYNC_FAILURES:
                # Repeated sync failures indicate that a full sync did not restore the 404 error, so terminate
                # syncing on this account altogether.
                self.email_account.is_authorized = False
                self.email_account.is_syncing = False
                self.email_account.save()
                logger.error('Repeated 404 error on incremental syncing. Authorization revoked for account %s' %
                             self.email_account)
            return

        self.connector.save_history_id()
        if not len(history):
            return

        new_messages = set()
        edit_labels = set()

        # Collect message ids for new, removed email messages and email messages with label changes.
        for history_item in history:
            logger.debug('parsing history %s' % history_item)

            # New email messages.
            if 'messagesAdded' in history_item:
                for item in history_item['messagesAdded']:
                    # Skip chat messages.
                    if 'labelIds' in item['message'] and settings.GMAIL_LABEL_CHAT not in item['message']['labelIds']:
                        logger.debug('Message added %s' % item['message']['id'])
                        new_messages.add(item['message']['id'])

            # Email messages with labels added.
            for message in history_item.get('labelsAdded', []):
                if settings.GMAIL_LABEL_CHAT in message['message']['labelIds']:
                    continue

                if message['message']['id'] not in new_messages:
                    logger.debug('message updated %s', message['message']['id'])
                    edit_labels.add(message['message']['id'])

            # Email messages with labels removed.
            for message in history_item.get('labelsRemoved', []):
                if 'labelIds' in message['message'] and settings.GMAIL_LABEL_CHAT in message['message']['labelIds']:
                    continue

                if message['message']['id'] not in new_messages:
                    logger.debug('message updated %s', message['message']['id'])
                    edit_labels.add(message['message']['id'])

            # Removed email messages.
            for message in history_item.get('messagesDeleted', []):
                logger.debug('deleting message %s' % message['message']['id'])

                # When deleting the message, there is no need anymore to create a download it or update its labels.
                new_messages.discard(message['message']['id'])
                edit_labels.discard(message['message']['id'])

                EmailMessage.objects.filter(
                    message_id=message['message']['id'], account=self.email_account
                ).order_by().delete()

        # Create tasks to download email messages.
        for message_id in new_messages:
            logger.info('creating download_email_message for %s', message_id)
            app.send_task('download_email_message', args=[self.email_account.id, message_id])

        # Creates tasks to update labeling for email messages.
        for message_id in edit_labels:
            logger.info('creating update_labels_for_message for %s', message_id)
            app.send_task('update_labels_for_message', args=[self.email_account.id, message_id])

        # Only update the unread count if the history id was updated.
        if old_history_id != self.email_account.history_id:
            # TODO: Find out if there is a better place to update unread count. download_email_message tasks aren't
            # finished yet.
            self.update_unread_count()

    def sync_labels(self):
        """
        Synchronize labels.

        Fetches all the labels for the email account.
        Add, remove and rename the labels in the database retrieved from the api.
        """

        # Get all labels from Google.
        api_labels = self.connector.get_label_list()
        # Get all labels from the database.
        db_labels = self.email_account.labels.all()

        # Create sets of the API and database labels.
        api_label_set = set(label['id'] for label in api_labels)
        db_label_set = set(label.label_id for label in db_labels)

        # Determine with set operations which labels to remove and which to create or update.
        create_label_ids = api_label_set - db_label_set  # Labels that exist in Gmail but not in our db.
        update_label_ids = api_label_set & db_label_set  # Labels that exist both in Gmail and in our db.
        delete_label_ids = db_label_set - api_label_set  # Labels that exist in our db but not in Gmail.

        # Apply database changes.
        if create_label_ids:
            bulk = []
            for api_label in api_labels:
                if api_label['id'] in create_label_ids:
                    label_type = EmailLabel.LABEL_SYSTEM if api_label['type'] == 'system' else EmailLabel.LABEL_USER
                    bulk.append(
                        EmailLabel(
                            account=self.email_account,
                            label_id=api_label['id'],
                            name=api_label['name'],
                            label_type=label_type
                        )
                    )

            EmailLabel.objects.bulk_create(bulk)

        if update_label_ids:
            # Use dict comprehension to get dictonaries with the label_id as the keys and
            api_label_dict = {label['id']: label['name'] for label in api_labels}  # the name as the value.
            db_label_dict = {label.label_id: label for label in db_labels}  # the label as the value.
            for label_id in update_label_ids:
                if api_label_dict[label_id] != db_label_dict[label_id].name:
                    # Only update labels with a changed name.
                    label = db_label_dict[label_id]
                    label.name = api_label_dict[label_id]
                    label.save()

        if delete_label_ids:
            # TODO: LILY-2342 Research that removing a label isn't deleting messages on cascade.
            EmailLabel.objects.filter(
                account=self.email_account,
                label_id__in=delete_label_ids
            ).delete()

    def update_unread_count(self):
        """
        Update unread count on every label.
        """
        pass
        # logger.debug('Updating unread count for every label, account %s' % self.email_account)
        # for label in self.email_account.labels.all():
        #     unread_count = label.messages.filter(read=False).count()
        #     label.unread = unread_count
        #     label.save()

    def administer_sync_status(self, is_syncing):
        """
        Keep track if the email account is synchronizing and reset synchronization failure count.
        """
        self.email_account.is_syncing = is_syncing
        self.email_account.sync_failure_count = 0
        self.email_account.save(update_fields=["is_syncing", "sync_failure_count"])

    def get_label(self, label_id, use_db=True):
        """
        Returns the label given the label_id.

        Args:
            label_id (string): label_id of the label
            use_db (bool): First try to retrieve the label from the database.

        Returns:
            EmailLabel instance
        """
        label = None

        if use_db:
            try:
                label = EmailLabel.objects.get(account=self.email_account, label_id=label_id)
            except EmailLabel.DoesNotExist:
                pass

        if not label:
            label_info = self.connector.get_label_info(label_id)
            label = self.label_builder.get_or_create_label(label_info)[0]

        return label

    def get_attachment(self, message_id, attachment_id):
        """
        Returns the attachment given the message_id and attachment_id

        Args:
            message_id (string): message_id of the message
            attachment_id (string): attachment_id of the message

        Returns:
            dict with attachment info
        """
        return self.connector.get_attachment(message_id, attachment_id)

    def update_labels_for_message(self, message_id):
        """
        Fetch the labels for the EmailMessage with the given message_id.

        Args:
            message_id (string): message_id of the message
        """
        try:
            email_message = EmailMessage.objects.get(message_id=message_id, account=self.email_account)
        except EmailMessage.DoesNotExist:
            self.download_message(message_id)
            return

        try:
            message_info = self.connector.get_short_message_info(message_id)
        except NotFoundError:
            return

        logger.debug('Storing label info for message: %s, account %s' % (
            message_id,
            self.email_account
        ))

        # Keep track if anything has changed.
        changed = False

        # Check if existing labels differ from new labels.
        existing_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        if not email_message.read:
            existing_labels.add(settings.GMAIL_LABEL_UNREAD)

        new_labels = set(message_info.get('labelIds', []))
        if len(new_labels ^ existing_labels):
            self.message_builder.store_labels_and_thread_for_message(message_info, message_id)
            changed = True

        elif email_message.thread_id != message_info['threadId']:
            self.message_builder.message.thread_id = message_info['threadId']
            changed = True

        # Labels or thread_id has changed, lets save.
        if changed:
            try:
                self.message_builder.save()
            except Exception:
                logger.exception(
                    'Couldn\'t save message %s for account %s' % (message_id, self.email_account))

    def add_and_remove_labels_for_message(self, email_message, add_labels=[], remove_labels=[]):
        """
        Add and/or removes labels from the EmailMessage.

        Args:
            email_message (instance): EmailMessage instance
            add_labels (list, optional): list of label_ids to add
            remove_labels (list, optional): list of label_ids to remove
        """
        # We should do some tries to update.
        for n in range(0, 6):
            try:
                message_info = self.connector.get_short_message_info(email_message.message_id)
            except NotFoundError:
                logger.debug('Message not available on remote.')
                EmailMessage.objects.get(pk=email_message.id).delete()
                return

            # Initialize a label update object.
            labels = {'addLabelIds': [], 'removeLabelIds': []}

            for label in add_labels:
                if label not in message_info.get('labelIds', []) and label != settings.GMAIL_LABEL_SENT:
                    if email_message.account.labels.filter(label_id=label).exists():
                        labels['addLabelIds'].append(label)

            for label in remove_labels:
                if label in message_info.get('labelIds', []) and label != settings.GMAIL_LABEL_SENT:
                    labels['removeLabelIds'].append(label)

            if labels['addLabelIds'] or labels['removeLabelIds']:
                # There actually are labels to add or remove.
                try:
                    self.connector.update_labels(email_message.message_id, labels)
                except LabelNotFoundError:
                    logger.error('label not found, update labels failed! %s: %s' %
                                 (self.email_account, email_message.message_id))
                except HttpError:
                    # Other than a label error, so raise.
                    logger.error('update labels failed! %s: %s' % (self.email_account, email_message.message_id))
                    raise
                else:
                    # API call to update labelling successfull, so also update the labelling in the database.
                    email_message.labels.remove(
                        *list(EmailLabel.objects.filter(label_id__in=labels['removeLabelIds'],
                                                        account=self.email_account))
                    )
                    email_message.labels.add(
                        *list(EmailLabel.objects.filter(label_id__in=labels['addLabelIds'],
                                                        account=self.email_account))
                    )
                    # Labels updated in the database, so no need to retry / continue the for-loop.
                    break

        self.update_unread_count()

    def toggle_star_email_message(self, email_message, star=True):
        """
        (Un)star a message.

        Args:
            email_message(instance): EmailMessage instance
            star (bool, optional): If True, star the message
        """
        add_labels = []
        remove_labels = []
        if star:
            add_labels = [settings.GMAIL_LABEL_STAR]
        else:
            remove_labels = [settings.GMAIL_LABEL_STAR]

        self.add_and_remove_labels_for_message(email_message, add_labels, remove_labels)

    def toggle_read_email_message(self, email_message, read=True):
        """
        Mark message as read or unread.

        Args:
            email_message(instance): EmailMessage instance
            read (bool, optional): If True, mark message as read
        """
        add_labels = []
        remove_labels = []

        if read:
            remove_labels = [settings.GMAIL_LABEL_UNREAD]
        else:
            add_labels = [settings.GMAIL_LABEL_UNREAD]

        self.add_and_remove_labels_for_message(email_message, add_labels, remove_labels)

    def toggle_spam_email_message(self, email_message, spam=True):
        """
        (Un)mark a message as spam.

        Args:
            email_message(instance): EmailMessage instance
            spam (bool, optional): If True, mark the message as spam
        """
        add_labels = []
        remove_labels = []

        if spam:
            add_labels = [settings.GMAIL_LABEL_SPAM]
            for label in email_message.labels.all():
                remove_labels.append(label.name)
        else:
            remove_labels = [settings.GMAIL_LABEL_SPAM]

        self.add_and_remove_labels_for_message(email_message, add_labels, remove_labels)

    def trash_email_message(self, email_message):
        """
        Trash current EmailMessage.

        Args:
            email_message (instance): EmailMessage instance
        """
        try:
            message_dict = self.connector.trash_email_message(email_message.message_id)
            # TODO: LILY-2320 Trashing is just updating the labels, so remove unnecessary api call to get the complete
            # message info again. Update is needed on the message builder.
            full_message_dict = self.connector.get_message_info(message_dict['id'])
        except NotFoundError:
            logger.debug('Message already deleted from remote')
        else:
            # Store updated message.
            self.message_builder.store_message_info(full_message_dict, message_dict['id'])
            self.message_builder.save()
            self.update_unread_count()

    def delete_email_message(self, email_message):
        """
        Delete current EmailMessage.

        Args:
            email_message (instance): EmailMessage instance
        """
        try:
            self.connector.delete_email_message(email_message.message_id)
        except NotFoundError:
            logger.debug('Message already deleted from remote')
        else:
            self.update_unread_count()

    def send_email_message(self, email_message, thread_id=None):
        """
        Send email.

        Args:
            email_message (instance): Email instance
            thread_id (string): Thread ID of original message that is replied or forwarded on
        """
        # Send message.
        message_dict = self.connector.send_email_message(email_message.as_string(), thread_id)
        try:
            full_message_dict = self.connector.get_message_info(message_dict['id'])
        except NotFoundError:
            logger.debug('Message already deleted from remote')
        else:
            # Store updated message.
            self.message_builder.store_message_info(full_message_dict, message_dict['id'])
            self.message_builder.save()
            self.update_unread_count()

    def create_draft_email_message(self, email_message):
        """
        Create email draft.

        Args:
            email_message (instance): Email instance
        """
        # Create draft message.
        draft_dict = self.connector.create_draft_email_message(email_message.as_string())

        try:
            message_dict = self.connector.get_message_info(draft_dict['message']['id'])
        except NotFoundError:
            logger.debug('Message already deleted from remote')
        else:
            # Store updated message.
            self.message_builder.store_message_info(message_dict, draft_dict['message']['id'])
            self.message_builder.message.draft_id = draft_dict.get('id', '')
            self.message_builder.save()
            self.update_unread_count()

    def update_draft_email_message(self, email_message, draft_id):
        """
        Update email draft.

        Args:
            email_message (instance): Email instance
            draft_id (string): id of current draft
        """
        # Update draft message.
        draft_dict = self.connector.update_draft_email_message(email_message.as_string(), draft_id)

        try:
            message_dict = self.connector.get_message_info(draft_dict['message']['id'])
        except NotFoundError:
            logger.debug('Message already deleted from remote')
        else:
            # Store updated message.
            self.message_builder.store_message_info(message_dict, draft_dict['message']['id'])
            self.message_builder.message.draft_id = draft_dict.get('id', '')
            self.message_builder.save()
            self.update_unread_count()

    def delete_draft_email_message(self, email_message):
        """
        Delete current draft.

        Args:
            email_message (instance): EmailMessage instance
        """
        try:
            self.connector.delete_draft_email_message(email_message.draft_id)
        except NotFoundError:
            # Draft exists in Lily but not anymore on remote, so remove it from the database.
            logger.debug('Draft already deleted from remote.')
            EmailMessage.objects.filter(message_id=email_message.message_id, account=self.email_account).delete()
        else:
            self.update_unread_count()

    def cleanup(self):
        """
        Cleanup references, to prevent reference cycle.
        """
        self.message_builder.cleanup()
        self.message_builder = None
        self.label_builder.cleanup()
        self.label_builder = None
        self.connector.cleanup()
        self.connector = None
        self.email_account = None

        gc.collect()
