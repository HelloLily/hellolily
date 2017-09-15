import csv
import gc
import logging
from datetime import date
from hashlib import sha256

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.urls import reverse_lazy

from lily.tenant.models import Tenant

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **kwargs):
        current_site = 'app.hellolily.com'

        with default_storage.open('beta_signups_with_invites.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(['company', 'email', 'first_name', 'last_name', 'invite', 'country'])

            for row in self.read_csvfile('beta_signups.csv'):
                company = row['company']
                first_name = row['first_name']
                last_name = row['last_name']
                email = row['email']
                country = row['country']
                date_string = date.today().strftime('%d%m%Y')

                tenant = Tenant.objects.create(name=company, country=country)

                call_command('create_tenant', tenant=tenant.id)

                invite_hash = sha256('%s-%s-%s-%s' % (
                    tenant.id,
                    email,
                    date_string,
                    settings.SECRET_KEY
                )).hexdigest()

                invite_link = '%s://%s%s' % ('https', current_site, reverse_lazy('invitation_accept', kwargs={
                    'tenant_id': tenant.id,
                    'first_name': first_name,
                    'email': email,
                    'date': date_string,
                    'hash': invite_hash,
                }))

                spamwriter.writerow([company, email, first_name, last_name, invite_link, country])

                gc.collect()

    def read_csvfile(self, file_name):
        """
        Read from path assuming it's a file with ';' separated values.
        """
        # Newlines are breaking correct csv parsing. Write correct temporary file to parse.
        csv_file = default_storage.open(file_name, 'rU')
        reader = csv.DictReader(csv_file, delimiter=';', quoting=csv.QUOTE_ALL)
        for row in reader:
            yield row
