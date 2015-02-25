import logging
from optparse import make_option
from django.core.management import BaseCommand

from ...manager import GmailManager, SyncLimitReached
from ...models.models import EmailAccount


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    SyncGmail syncs email account given the email address.

    Args:
        email_address: email address from account

    Optional arguments:
        --limit=<int>: Limit sync to this amount of emails
        --full-sync: full update of email-account
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--limit',
            action='store',
            nargs=1,
            dest='limit',
            default=None,
            help='Limit sync to this amount of emails'
        ),
        make_option(
            '--full-sync',
            action='store_true',
            dest='full-sync',
            help='Force full sync of account'
        ),
    )

    def handle(self, email_address, **options):
        email_account = EmailAccount.objects.get(email_address=email_address)
        try:
            limit = options.get('limit', None)
            if limit:
                limit = int(limit)
            full_sync = False if not options['full-sync'] else True
            manager = GmailManager(email_account)
            manager.synchronize(limit=limit, full_sync=full_sync)
        except SyncLimitReached:
            pass
