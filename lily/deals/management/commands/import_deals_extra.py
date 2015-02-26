import csv
import gc
import logging
import os

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

from django.core.management.base import BaseCommand
from lily.deals.models import Deal


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
        Import oppertunities from sugar
        """

    user_mapping = {}
    deal_mapping = {}
    unmatched_deals = 0
    matched_deals = 0

    def handle(self, csvfile, tenant_pk, **kwargs):
        self.tenant_pk = tenant_pk

        # Get user mapping from env vars
        user_string = os.environ.get('USERMAPPING')
        for user in user_string.split(';'):
            sugar, lily = user.split(':')
            self.user_mapping[sugar] = lily

        for row in self.read_csvfile(csvfile):
            self._update_deal(row)
            gc.collect()

        logger.info('unmatched deals: %s' % self.unmatched_deals)
        logger.info('matched deals: %s' % self.matched_deals)
        logger.info('adding extra deal info finished')

    def read_csvfile(self, file_name):
        """
        Read from path assuming it's a file with ',' separated values.
        """
        csv_file = default_storage.open(file_name, 'rU')

        # Find header from csv file
        sample = csv_file.read(2048)
        dialect = csv.Sniffer().sniff(sample)
        csv_file.seek(0)

        reader = csv.DictReader(csv_file, dialect=dialect)
        for row in reader:
            yield row

    def _update_deal(self, values):

        column_attribute_mapping = {
            # '"twittersatus_c"',
            '"id_c"': 'import_id',
            # '"why_client_c"',
            'amount_once_c': 'amount_once',
            # '"lost_extra_infro_c"',
            'amount_month_c': 'amount_recurring',
            # 'cardsend_c',
            'feedbackform_c': 'feedback_form_sent',
            'amount_hardware_c': 'amount_hardware',
            # '"oppertunity_reason_loss_c"': ,
        }

        # Get Deal
        deal_kwargs = dict()
        for column, value in values.items():
            if value and column in column_attribute_mapping:
                attribute = column_attribute_mapping.get(column)
                deal_kwargs[attribute] = value

        deal_kwargs['import_id'] = deal_kwargs['import_id'][1:-1]
        try:
            deal = Deal.objects.get(tenant_id=self.tenant_pk, import_id=deal_kwargs['import_id'])
        except Deal.DoesNotExist:
            self.unmatched_deals += 1
            logger.warning('deal doesn\'t exists %s' % deal_kwargs['import_id'])
            return

        for k, v in deal_kwargs.items():
            setattr(deal, k, v)

        try:
            deal.save()
            self.matched_deals += 1
        except ValidationError:
            self.unmatched_deals += 1
