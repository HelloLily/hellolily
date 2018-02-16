from django.db import transaction

from email_wrapper_lib.models.models import (
    EmailMessage, EmailRecipient, EmailMessageToEmailRecipient, EmailMessageToEmailFolder
)


recipient_types_with_id = (
        ('to', EmailMessageToEmailRecipient.TO),
        ('cc', EmailMessageToEmailRecipient.CC),
        ('bcc', EmailMessageToEmailRecipient.BCC),
        ('from', EmailMessageToEmailRecipient.FROM),
        ('sender', EmailMessageToEmailRecipient.SENDER),
        ('reply_to', EmailMessageToEmailRecipient.REPLY_TO),
    )


def create_messages(account, messages_to_create):
    unsaved_message_list = []

    db_folders = {folder[0]: folder[1] for folder in account.folders.all().values_list('remote_id', 'id')}
    unsaved_message_to_folder_list = []

    db_recipients = {rec[0]: rec[1] for rec in EmailRecipient.objects.all().values_list('raw_value', 'id')}
    unsaved_recipients_by_raw_value = {}
    unsaved_message_to_recipient_list = []

    for message in messages_to_create:
        folders = message.data.pop('folders', [])
        recipients = message.data.pop('recipients')

        unsaved_message = EmailMessage(account=account, **message.data)
        unsaved_message_list.append(unsaved_message)

        for remote_folder_id in folders:
            # TODO: maybe add logic to create a Folder if it doesn't exist yet.
            unsaved_message_to_folder = EmailMessageToEmailFolder(
                emailmessage=unsaved_message,
                emailfolder_id=db_folders[remote_folder_id]
            )
            unsaved_message_to_folder_list.append(unsaved_message_to_folder)

        for recipient_type, recipient_type_id in recipient_types_with_id:
            for recipient in recipients.get(recipient_type, []):
                # Loop over every recipient type in the message.
                if recipient['raw_value'] in db_recipients.keys():
                    # Recipient already exists, use it.
                    unsaved_message_to_recipient = EmailMessageToEmailRecipient(
                        message=unsaved_message,
                        recipient_id=db_recipients[recipient['raw_value']],
                        recipient_type=recipient_type_id
                    )
                    unsaved_message_to_recipient_list.append(unsaved_message_to_recipient)
                else:
                    # Recipient is new or already queued for creation.
                    if recipient['raw_value'] in unsaved_recipients_by_raw_value.keys():
                        # Recipient is created previously in the batch, link to that one.
                        unsaved_recipient = unsaved_recipients_by_raw_value[recipient['raw_value']]
                    else:
                        # Recipient is new, create it.
                        unsaved_recipient = EmailRecipient(**recipient)
                        unsaved_recipients_by_raw_value[recipient['raw_value']] = unsaved_recipient

                    unsaved_message_to_recipient = EmailMessageToEmailRecipient(
                        message=unsaved_message,
                        recipient=unsaved_recipient,
                        recipient_type=recipient_type_id
                    )
                    unsaved_message_to_recipient_list.append(unsaved_message_to_recipient)

    with transaction.atomic():
        EmailMessage.objects.bulk_create(unsaved_message_list)
        EmailRecipient.objects.bulk_create(unsaved_recipients_by_raw_value.values())

        for item in unsaved_message_to_folder_list:
            if not item.emailmessage_id:
                item.emailmessage = item.emailmessage

        for item in unsaved_message_to_recipient_list:
            # Hack to set the message_id and recipient_id properties after they've been created.
            # Without this the _ids will be empty and an sql error will be thrown, even though the objects exist.
            if not item.message_id:
                item.message = item.message

            if not item.recipient_id:
                item.recipient = item.recipient

        EmailMessageToEmailFolder.objects.bulk_create(unsaved_message_to_folder_list)
        EmailMessageToEmailRecipient.objects.bulk_create(unsaved_message_to_recipient_list)


def update_messages(account, messages_to_update):
    pass
