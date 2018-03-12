from django.db import transaction, IntegrityError

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


def create_messages(account, message_promise_list):
    # Recipients are not account specific, so db errors can occur when multiple tasks try to save at the same time.
    # Build a cache of recipients already in the db.
    # TODO: make sure that if the recipient table is really big, this is still fast.
    db_recipients = {rec[0]: rec[1] for rec in EmailRecipient.objects.all().values_list('raw_value', 'id')}

    # Filter out empty promises.
    # There is a bug between gmail/apple that creates empty messages.
    # More info: https://productforums.google.com/forum/#!topic/gmail/WyTczFXSjh0
    message_promise_list = [msg_promise for msg_promise in message_promise_list if msg_promise.data]

    for promise in message_promise_list:
        recipients = promise.data.get('recipients', {})

        for recipient_type, recipient_type_id in recipient_types_with_id:
            # Loop over every recipient type in the message.
            for recipient in recipients.get(recipient_type, []):
                if recipient['raw_value'] not in db_recipients.keys():
                    # The recipient was not found in the database, so try to create it.
                    try:
                        rec = EmailRecipient.objects.create(**recipient)
                    except IntegrityError:
                        rec = EmailRecipient.objects.get(raw_value=recipient['raw_value'])

                    # Add the recipient to the list and dict.
                    db_recipients[recipient['raw_value']] = rec.pk

    # Prepare to bulk create new messages and their folder/recipient relations.
    db_folders = {folder[0]: folder[1] for folder in account.folders.all().values_list('remote_id', 'id')}

    unsaved_message_list = []
    unsaved_message_to_folder_list = []
    unsaved_message_to_recipient_list = []

    for promise in message_promise_list:
        folders = promise.data.pop('folders', [])
        recipients = promise.data.pop('recipients', [])

        unsaved_message = EmailMessage(account=account, **promise.data)
        unsaved_message_list.append(unsaved_message)

        for remote_folder_id in folders:
            # TODO: maybe add logic to create a Folder if it doesn't exist yet.
            unsaved_message_to_folder = EmailMessageToEmailFolder(
                emailmessage=unsaved_message,
                emailfolder_id=db_folders[remote_folder_id]
            )
            unsaved_message_to_folder_list.append(unsaved_message_to_folder)

        # Create the relation between message and recipients per recipient_type.
        for recipient_type, recipient_type_id in recipient_types_with_id:
            for recipient in recipients.get(recipient_type, []):
                unsaved_message_to_recipient = EmailMessageToEmailRecipient(
                    message=unsaved_message,
                    recipient_id=db_recipients[recipient['raw_value']],
                    recipient_type=recipient_type_id
                )
                unsaved_message_to_recipient_list.append(unsaved_message_to_recipient)

    with transaction.atomic():
        EmailMessage.objects.bulk_create(unsaved_message_list)

        for item in unsaved_message_to_folder_list:
            if not item.emailmessage_id:
                item.emailmessage = item.emailmessage

        for item in unsaved_message_to_recipient_list:
            # Hack to set the message_id and recipient_id properties after they've been created.
            # Without this the _ids will be empty and an sql error will be thrown, even though the objects exist.
            if not item.message_id:
                item.message = item.message

        EmailMessageToEmailFolder.objects.bulk_create(unsaved_message_to_folder_list)
        EmailMessageToEmailRecipient.objects.bulk_create(unsaved_message_to_recipient_list)


def update_messages(account, message_data):
    pass


def delete_messages(account, message_ids):
    pass
