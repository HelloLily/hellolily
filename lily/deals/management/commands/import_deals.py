import csv
import gc
import logging
import os

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

from django.core.management.base import BaseCommand
from lily.deals.models import Deal


logger = logging.getLogger(__name__)

CURRENCY = 'EUR'

class Command(BaseCommand):
    help = """
        Import oppertunities from sugar
        """

    user_mapping = {}
    deal_mapping = {}
    stage_mapping = {
        'Negotiation/Review': Deal.LOST_STAGE,
        'Needs Analysis': Deal.LOST_STAGE,
        'Perception Analysis': Deal.LOST_STAGE,
        'Closed Won': Deal.WON_STAGE,
        'MailSend': Deal.EMAILED_STAGE,
        None: Deal.LOST_STAGE,
        'Closed Lost': Deal.LOST_STAGE,
        'Prospecting': Deal.LOST_STAGE,
        'Proposal/Price Quote': Deal.PENDING_STAGE,
        'Called': Deal.CALLED_STAGE,
        'Special': Deal.EMAILED_STAGE,
    }

    def handle(self, csvfile, tenant_pk, **kwargs):
        self.tenant_pk = tenant_pk

        # Get user mapping from env vars
        user_string = os.environ.get('USERMAPPING')
        for user in user_string.split(';'):
            sugar, lily = user.split(':')
            self.user_mapping[sugar] = lily

        for row in self.read_csvfile(csvfile):
            self._create_deal(row)
            gc.collect()

        logger.info('importing deals finished')

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

    def _create_deal(self, values):

        column_attribute_mapping = {
            'date_closed': 'closed_date',
            # 'next_step',
            # 'modified_user_id',
            'date_entered': 'created',
            'name': 'name',
            # 'probability',
            # 'date_modified',
            'deleted': 'is_deleted',
            # 'opportunity_type',
            # 'campaign_id',
            # 'created_by',
            # 'currency_id': 'currency',
            # 'lead_source',
            # 'amount',
            # 'sales_stage': 'stage',
            # 'assigned_user_id': 'import_user_id',
            # 'amount_usdollar',
            'id': 'import_id',
            'description': 'description',
        }

        # Create deal
        deal_kwargs = dict()
        for column, value in values.items():
            if value and column in column_attribute_mapping:
                attribute = column_attribute_mapping.get(column)
                deal_kwargs[attribute] = value

        deal_kwargs['stage'] = self.stage_mapping.get(values.get('sales_stage', None))
        deal_kwargs['currency'] = CURRENCY

        try:
            deal = Deal.objects.get(tenant_id=self.tenant_pk, import_id=deal_kwargs['import_id'])
        except Deal.DoesNotExist:
            deal = Deal(tenant_id=self.tenant_pk)
        else:
            import pdb
            pdb.set_trace()
            if deal.modified > values['date_modified']:
                return

        for k, v in deal_kwargs.items():
            setattr(deal, k, v)

        deal.closed_date == '1970-01-01' if deal.closed_date == '0000-00-00' else deal.closed_date
        deal.is_deleted = False if deal.is_deleted == '0' else True

        try:
            deal.save()
        except ValidationError, e:
            logger.warning('cannot save deal:%s\n %s' % (e, values))
            pass
