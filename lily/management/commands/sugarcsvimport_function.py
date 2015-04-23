import csv
import logging

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Import functions from combined csv file.

E.g.:
* sugarcsvimport_function /local/sandbox/hellolily-import/functions.csv  10
"""

    def handle(self, csvfile, tenant_pk, **kwargs):
        self.tenant_pk = tenant_pk

        csv_file = default_storage.open(csvfile, 'rU')
        reader = csv.DictReader(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
        for row in reader:
            self._create_function_data(row)

    def _create_function_data(self, values):
        """
        Create Function from given dict.

        Arguments:
            values (dict): information with function information
        """
        contact_id = values.get('Contact ID')
        account_id = values.get('Account ID')
        is_deleted = values.get('Deleted')
        title = values.get('Title') + " " + values.get("Department")

        try:
            contact = Contact.objects.get(tenant_id=self.tenant_pk, import_id=contact_id)
        except Contact.DoesNotExist:
            logger.error('Contact does not exist %s', values)
            return

        try:
            account = Account.objects.get(tenant_id=self.tenant_pk, import_id=account_id)
        except Account.DoesNotExist:
            logger.error('Account does not exist %s', values)
            return

        # UPDATE!!
        Function.objects.get_or_create(
            contact=contact,
            account=account,
            is_deleted=is_deleted
        )
