import logging

from django.core.management import BaseCommand

from ...tasks import send_message
from ...models.models import EmailOutboxMessage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Resend en emailmessage that is stuck in the outbox table

           E.g.:
           * resend_email 1427
           Where 1427 is the ID of the emailoutboxmessage record
           """

    def handle(self, outboxmessage_id, **kwargs):
        out_id = int(outboxmessage_id)

        logger.info('Resending email %d' % out_id)

        try:
            EmailOutboxMessage.objects.get(pk=out_id)
        except EmailOutboxMessage.DoesNotExist:
            logger.error('There is no outbox message for id %d' % out_id)
        else:
            succes = send_message(out_id)
            logger.info('Resending with status %s for resending email %d' % (succes, out_id))
