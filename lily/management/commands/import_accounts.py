import csv
import gc

from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from lily.accounts.models import Account, AccountStatus, Website
from lily.tags.models import Tag
from lily.tenant.models import Tenant
from lily.utils.models.models import EmailAddress


class Command(BaseCommand):
    help = """
        Import accounts.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant', action='store', dest='tenant', default='', help='Specify a tenant to import the accounts for.'
        )
        parser.add_argument(
            '--tag',
            action='store',
            dest='tag',
            default='',
            help='Specify the tag you wish to apply to the imported accounts or leave blank.'
        )

    def handle(self, csvfile, *args, **options):
        tenant_id = options['tenant'].strip()
        tag_name = options['tag'].replace('_', ' ')

        if tag_name:
            content_type = ContentType.objects.get_for_model(Account)

        if tenant_id:
            tenant = Tenant.objects.get(pk=int(tenant_id))
        else:
            raise Exception('Please provide the ID of the tenant you wish to import accounts for.')

        for row in self.read_csvfile(csvfile):
            name = row.get('name')
            account_status = AccountStatus.objects.get(name='Prospect', tenant=tenant)
            account = Account.objects.create(name=name, tenant=tenant, status=account_status)

            website = Website.objects.create(
                website=row.get('website'),
                is_primary=True,
                account=account,
                tenant=tenant,
            )

            email_address = EmailAddress.objects.create(
                email_address=row.get('email_address'),
                status=EmailAddress.PRIMARY_STATUS,
                tenant=tenant,
            )

            if tag_name:
                tag = Tag.objects.create(
                    name=tag_name,
                    object_id=account.id,
                    content_type=content_type,
                    tenant=tenant,
                )

            account.email_addresses.add(email_address)
            account.websites.add(website)
            account.tags.add(tag)

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
