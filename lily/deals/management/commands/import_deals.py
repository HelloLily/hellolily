import csv
import gc
import logging
import os
from decimal import Decimal
from datetime import datetime, timedelta

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.utils import timezone

from lily.deals.models import Deal
from lily.users.models import LilyUser

logger = logging.getLogger(__name__)

CURRENCY = 'EUR'


class Command(BaseCommand):
    help = """
        Import oppertunities from sugar
        """

    user_mapping = {}
    already_logged = set()
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
    column_attribute_mapping = {
        'ID': 'import_id',
        'Name': 'name',
        'Date Created': 'created',
        'Description': 'description',
        'Feedback Form Send?': 'feedback_form_sent',
    }
    type_mapping = {
        'New Business': True,
        'Existing Business': False,
        # Default from model
        None: False,
    }

    def handle(self, csvfile, tenant_pk, **kwargs):
        self.tenant_pk = tenant_pk
        logger.info('Starting deals import')
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

        try:
            # Create deal
            deal_kwargs = dict()
            for column, value in values.items():
                if value and column in self.column_attribute_mapping:
                    attribute = self.column_attribute_mapping.get(column)
                    # Set created date to original created date in sugar.
                    if attribute == 'created':
                        value = timezone.make_aware(
                            datetime.strptime(str(value), "%d-%m-%Y %H.%M"), timezone.get_current_timezone()
                        )
                    deal_kwargs[attribute] = value

            eenmalig = 0.00
            if values.get('Eenmalig') is not None:
                eenmalig = Decimal(values.get('Eenmalig').decode('utf-8').replace(u'\u20ac', '').replace(',', ''))

            maandelijks = 0.00
            if values.get('Maandelijks') is not None:
                maandelijks = Decimal(
                    values.get('Maandelijks').decode('utf-8').replace(u'\u20ac', '').replace(',', '')
                )

            hardware = 0.00
            if values.get('Hardware') is not None:
                hardware = Decimal(values.get('Hardware').decode('utf-8').replace(u'\u20ac', '').replace(',', ''))

            amount = 0.00
            if values.get('Opportunity Amount') is not None:
                amount = Decimal(
                    values.get('Opportunity Amount').decode('utf-8').replace(u'\u20ac', '').replace(',', '')
                )

            deal_kwargs['amount_once'] = (eenmalig + hardware) if (eenmalig > 0.00 or hardware > 0.00) else amount
            deal_kwargs['amount_recurring'] = maandelijks

            deal_kwargs['type'] = self.type_mapping.get(values.get('Type', None))
            deal_kwargs['stage'] = self.stage_mapping.get(values.get('Sales Stage', None))
            deal_kwargs['feedback_form_sent'] = True if values.get('Feedback Form Send?') == '1' else False
            deal_kwargs['currency'] = CURRENCY

            try:
                deal = Deal.objects.get(tenant_id=self.tenant_pk, import_id=deal_kwargs['import_id'])
                # Set logic here for what you want to import when rerunning the import
                # Check wiki for last import date to filter any changed deals after the import
                return
            except Deal.DoesNotExist:
                deal = Deal(tenant_id=self.tenant_pk)

                for k, v in deal_kwargs.items():
                    setattr(deal, k, v)

                deal.is_archived = True

                some_time_ago = timezone.make_aware((datetime.now() - timedelta(6 * 365 / 12)),
                                                    timezone.get_current_timezone())

                is_special = values.get('Sales Stage', '') == 'Special'
                if is_special and deal.created > some_time_ago:
                    deal.is_archived = False

                is_closed_won = values.get('Sales Stage', None) not in ('Closed Won', 'Closed Lost')

                if is_closed_won and deal.created > some_time_ago:
                    deal.is_archived = False

                user_id = values.get('Assigned User ID')
                if user_id and user_id in self.user_mapping:
                    try:
                        deal.assigned_to = LilyUser.objects.get(
                            pk=self.user_mapping[user_id], tenant_id=self.tenant_pk
                        )
                    except LilyUser.DoesNotExist:
                        if user_id not in self.already_logged:
                            self.already_logged.add(user_id)
                            logger.warning(u'Assignee does not exists as an LilyUser. %s' % user_id)
                else:
                    # Only log when user_name not empty.
                    if user_id and user_id not in self.already_logged:
                        self.already_logged.add(user_id)
                        logger.warning(u'Assignee does not have an usermapping. %s' % user_id)

            try:
                deal.save()
            except Exception as e:
                logger.warning('cannot save deal:%s\n %s' % (e, values))

        except Exception as e:
            logger.warning('Error importing row:%s\n %s' % (e, values))
