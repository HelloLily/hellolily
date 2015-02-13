from django.core.management import BaseCommand

from ...manager import GmailManager
from ...models import EmailAccount


class Command(BaseCommand):
    help = """
    GetMail Fetches email message from gmail api.

    Sets a pdb after creating message, before saving the message to db.
    Easy vars after pdb:
        message: EmailMessage instance
        builder: MessageBuilder instance

    Store message to db with builder.save()

    Args:
        email_address: email address where emailmessage is stored in
        message_id: id of the message
    """

    def handle(self, email_address, message_id, **kwargs):
        email_account = EmailAccount.objects.get(email_address=email_address)

        manager = GmailManager(email_account)
        message, created = manager.message_builder.get_or_create_message({'id': message_id, 'threadId': message_id})
        message_info = manager.connector.get_message_info(message_id)
        manager.message_builder.store_message_info(message_info)
        builder = manager.message_builder

        import pdb
        pdb.set_trace()
