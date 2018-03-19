import logging

from django.db import transaction, IntegrityError

from email_wrapper_lib.models.models import (
    EmailMessage, EmailRecipient, EmailMessageToEmailRecipient, EmailMessageToEmailFolder, EmailFolder
)


logger = logging.getLogger(__name__)


recipient_types_with_id = (
    ('to', EmailMessageToEmailRecipient.TO),
    ('cc', EmailMessageToEmailRecipient.CC),
    ('bcc', EmailMessageToEmailRecipient.BCC),
    ('from', EmailMessageToEmailRecipient.FROM),
    ('sender', EmailMessageToEmailRecipient.SENDER),
    ('reply_to', EmailMessageToEmailRecipient.REPLY_TO),
)


def save_new_folders(account_id, folder_list):
    EmailFolder.objects.bulk_create(
        [EmailFolder(account_id=account_id, **folder) for folder in folder_list]
    )


def save_updated_folders(account_id, folder_list):
    folder_dict = {
        f.remote_id: f for f in EmailFolder.objects.filter(account_id=account_id)
    }

    for folder in folder_list:
        db_folder = folder_dict[folder.get('remote_id')]

        editable_attrs = [
            'remote_value', 'name', 'messages_count', 'messages_unread_count', 'threads_count',
            'threads_unread_count', 'parent_id',
        ]

        if any([getattr(db_folder, attr_name) != folder.get(attr_name) for attr_name in editable_attrs]):
            # There was an actual change to the folder, so we need to update it.
            for attr in editable_attrs:
                setattr(db_folder, attr, folder[attr])

            db_folder.save(update_fields=editable_attrs)


def save_deleted_folders(account_id, folder_ids):
    EmailFolder.objects.filter(
        account_id=account_id,
        remote_id__in=folder_ids
    ).delete()


def save_new_messages(account_id, message_list):
    # Create cache dicts to speed things up.
    folder_dict = {
        f[0]: f[1] for f in EmailFolder.objects.filter(account_id=account_id).values_list('remote_id', 'id')
    }

    for message_data in message_list:
        recipient_dict = {
            rec[0]: rec[1] for rec in EmailRecipient.objects.all().values_list('raw_value', 'id')
        }

        # Pop related data before constructing a message.
        recipient_data = message_data.pop('recipients', {})
        folder_list = message_data.pop('folders', [])

        # Construct a message instance, to be saved later.
        message = EmailMessage(account_id=account_id, **message_data)

        # Save recipients.
        new_recipients = {}  # remote_id: recipient.
        message_to_recipient_list = []
        for recipient_type, recipient_type_id in recipient_types_with_id:
            for recipient in recipient_data.get(recipient_type, {}):
                if recipient['raw_value'] in recipient_dict.keys():
                    recipient_id = recipient_dict[recipient['raw_value']]

                    message_to_recipient_list.append(EmailMessageToEmailRecipient(
                        message=message,
                        recipient_id=recipient_id,
                        recipient_type=recipient_type_id
                    ))
                else:
                    if recipient['raw_value'] in new_recipients.keys():
                        # The recipient was created previously in the loop.
                        rec = new_recipients[recipient['raw_value']]
                    else:
                        # It's a new recipient, so add it to the new_recipients.
                        rec = EmailRecipient(**recipient)
                        new_recipients[rec.raw_value] = rec

                    message_to_recipient_list.append(EmailMessageToEmailRecipient(
                        message=message,
                        recipient=rec,
                        recipient_type=recipient_type_id
                    ))

        # Save all new recipients.
        EmailRecipient.objects.bulk_create(new_recipients.values())

        # Construct message to folder relations.
        message_to_folder_list = []
        for folder_id in folder_list:
            unsaved_message_to_folder = EmailMessageToEmailFolder(
                emailmessage=message,
                emailfolder_id=folder_dict[folder_id]
            )
            message_to_folder_list.append(unsaved_message_to_folder)

        try:
            with transaction.atomic():
                # Save message.
                message.save()
                # Hack to set the *_id properties of relations after they've been created.
                # Without this the *_ids will be empty and an sql error will be thrown, even though the objects exist.
                for item in message_to_folder_list:
                    item.emailmessage = item.emailmessage

                for item in message_to_recipient_list:
                    item.message = item.message
                    item.recipient = item.recipient

                # Save message to recipient relations.
                EmailMessageToEmailRecipient.objects.bulk_create(message_to_recipient_list)
                # Save message to folder relations.
                EmailMessageToEmailFolder.objects.bulk_create(message_to_folder_list)
        except Exception:
            logger.exception('Caught exception while saving the new messages.')


def save_updated_messages(account_id, message_list):
    # Create cache dict to speed things up.
    message_dict = {
        # TODO: filter on message_ids?
        m[0]: m[1] for m in EmailMessage.objects.filter(account_id=account_id).values_list('remote_id', 'id')
    }
    folder_dict = {
        f[0]: f[1] for f in EmailFolder.objects.filter(account_id=account_id).values_list('remote_id', 'id')
    }

    for message_data in message_list:
        message_id = message_dict[message_data['remote_id']]

        try:
            with transaction.atomic():
                EmailMessage.objects.filter(id=message_id).update(
                    is_read=message_data['is_read'],
                    is_starred=message_data['is_starred']
                )
                EmailMessageToEmailFolder.objects.filter(emailmessage_id=message_id).delete()
                EmailMessageToEmailFolder.objects.bulk_create([EmailMessageToEmailFolder(
                    emailmessage_id=message_id,
                    emailfolder_id=folder_dict[folder_id]
                ) for folder_id in message_data['folders']])
        except Exception:
            logger.exception('Caught exception while saving the updated messages.')


def save_deleted_messages(account_id, message_ids):
    try:
        EmailMessage.objects.filter(
            account_id=account_id,
            remote_id__in=message_ids
        ).delete()
    except Exception:
        logger.exception('Caught exception while deleting the deleted messages.')
