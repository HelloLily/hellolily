import csv
import gc
import logging

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import connection

from lily.deals.models import Deal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Load deal IDs from the given CSV and fix the modified date based on the date in the file."""

    deals = Deal.objects.all()
    total_modified_deals = 0

    def handle(self, csvfile, **kwargs):
        for row in self.read_csvfile(csvfile):
            self._update_modified_date(row)
            gc.collect()

        logger.info('Modified date of %s deals has been updated' % self.total_modified_deals)

    def read_csvfile(self, file_name):
        """
        Read from path assuming it's a file with ',' separated values.
        """
        csv_file = default_storage.open(file_name, 'rU')
        reader = csv.DictReader(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
        for row in reader:
            yield row

    def _update_modified_date(self, values):
        cursor = connection.cursor()
        cursor.execute("UPDATE deals_deal SET modified = %s WHERE id = %s", [values.get('modified'), values.get('id')])

        self.total_modified_deals += 1
