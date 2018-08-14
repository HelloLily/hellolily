import logging
import traceback
from django.core.management import BaseCommand

from ...manager import GmailManager
from ...models.models import EmailAccount

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Synclabels syncs the labels, threadId and snippets for all email accounts.
    """

    def handle(self, **options):
        email_accounts = EmailAccount.objects.filter(is_deleted=False, is_authorized=True)

        number_of_accounts = email_accounts.count()
        for index, email_account in enumerate(email_accounts):
            logger.info('syncing labels for %s (%s/%s)' % (
                email_account,
                index + 1,
                number_of_accounts,
            ))
            manager = None
            try:
                manager = GmailManager(email_account)
                manager.synchronize()
            except Exception, e:
                logger.error(traceback.format_exc(e))
                raise
            finally:
                if manager:
                    manager.cleanup()

            logger.info('sync done for %s (%s/%s)' % (email_account, index + 1, number_of_accounts))
