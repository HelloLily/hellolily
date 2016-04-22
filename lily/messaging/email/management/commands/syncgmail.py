from django.core.management import BaseCommand

from lily.messaging.email.manager import GmailManager
from lily.messaging.email.models.models import EmailAccount


class Command(BaseCommand):
    help = """
    SyncGmail syncs email account given the primary key.

    Args:
        pk: Primary key from account
    """

    def handle(self, pk, **options):
        email_account = EmailAccount.objects.get(pk=pk)
        manager = GmailManager(email_account)
        manager.full_synchronize()
