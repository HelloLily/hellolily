import csv
import gc
import logging

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

from django.core.management.base import BaseCommand
from lily.accounts.models import Account
from lily.deals.models import Deal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
        Import oppertunities from sugar
        """

    unmatched_deals = 0
    matched_deals = 0
    unknown_accounts = 0
    unknown_deals = 0
    validation_error = 0
    tenant_pk = None

    def handle(self, csvfile, tenant_pk, **kwargs):
        self.tenant_pk = tenant_pk

        logger.info('linking deals to accounts started')

        for row in self.read_csvfile(csvfile):
            self._update_deal(row)
            gc.collect()

        logger.info('unmatched deals: %s' % self.unmatched_deals)
        logger.info('matched deals: %s' % self.matched_deals)
        logger.info('unknown_accounts: %s' % self.unknown_accounts)
        logger.info('unknown_deals: %s' % self.unknown_deals)
        logger.info('validation_error: %s' % self.validation_error)
        logger.info('linking deals to accounts finished')

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
        if values.get('Deleted') == '1':
            return

        try:
            deal = Deal.objects.get(tenant_id=self.tenant_pk, import_id=values.get('Opportunity ID'))
        except Deal.DoesNotExist:
            self.unmatched_deals += 1
            self.unknown_deals += 1
            logger.warning('deal doesn\'t exists: %s' % values.get('Opportunity ID'))
            return

        try:
            account = Account.objects.get(tenant_id=self.tenant_pk, import_id=values.get('Account ID'))
        except Account.DoesNotExist:
            self.unmatched_deals += 1
            self.unknown_accounts += 1
            logger.warning('account doesn\'t exists: %s' % values.get('Account ID'))
            deal.delete()
            return

        deal.account = account

        try:
            deal.save()
            self.matched_deals += 1
        except ValidationError:
            deal.delete()
            self.unmatched_deals += 1
            self.validation_error += 1
