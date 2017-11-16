import csv
import gc
import logging
from datetime import date
from hashlib import sha256

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **kwargs):
        current_site = 'app.hellolily.com'

        for row in self.read_csvfile('alpha_users.csv'):
            first_name = row['first_name']
            email = row['email']
            tenant_id = row['tenant']
            date_string = date.today().strftime('%d%m%Y')

            invite_hash = sha256('%s-%s-%s-%s' % (
                tenant_id,
                email,
                date_string,
                settings.SECRET_KEY
            )).hexdigest()

            invite_link = '%s://%s%s' % ('https', current_site, reverse_lazy('invitation_accept', kwargs={
                'tenant_id': tenant_id,
                'first_name': first_name,
                'email': email,
                'date': date_string,
                'hash': invite_hash,
            }))

            print invite_link

            gc.collect()

    def read_csvfile(self, file_name):
        """
        Read from path assuming it's a file with ',' separated values.
        """
        # Newlines are breaking correct csv parsing. Write correct temporary file to parse.
        csv_file = default_storage.open(file_name, 'rU')
        reader = csv.DictReader(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
        for row in reader:
            yield row
