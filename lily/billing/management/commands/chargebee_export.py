from datetime import datetime
from decimal import Decimal
import csv
import gc
import logging
import operator

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from lily.billing.models import BillingInvoice
from lily.tenant.models import Tenant

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def get_code(self, tenant_id):
        # Twinfield requires the code to start with '1'.
        # After that we have a string with the tenant ID.
        # If the tenant ID is less than 4 characters we fill with 0's
        # until we're at 4 characters.
        return '1' + str(tenant_id).zfill(4)

    def handle(self, **kwargs):
        with default_storage.open('twinfield_customers.csv', 'wb') as csvfile:
            # Not all columns` have to be filled in, but Twinfield does require all columns to be present.
            twinfield_colums = [
                'code', 'name', 'website', 'defaultaddress', 'addresstype', 'Companyname', 'Attentionof',
                'addressline1', 'addressline2', 'postcode', 'City', 'country', 'telephone', 'fax', 'VATno', 'CoRegno',
                'emailaddress', 'collection', 'collectioncode', 'mandateinfo', 'firstcollection', 'signaturedate',
                'defaultbank', 'Accountholder', 'accountnumber', 'IBAN', 'BICcode', 'NationalBankID', 'Bankname',
                'bankaddress', 'bankaddressnumber', 'bankpostalcode', 'banklocation', 'bankstate', 'Reference',
                'bankcountry', 'duedays', 'ebilling', 'ebillingemailadress', 'generalledgeraccount', 'creditlimit',
                'creditmanager', 'blocked', 'authorised', 'segmentcode', 'remind', 'reminderemailaddress', 'comment',
                'discountitem', 'Sendtype', 'Emailaddress'
            ]

            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(twinfield_colums)

            for row in self.read_csvfile('Customers.csv'):
                # TODO Fetch latest customers.

                customer_id = row['Customer Id']

                if not customer_id:
                    continue

                try:
                    tenant = Tenant.objects.get(billing__customer_id=customer_id)
                except Tenant.DoesNotExist:
                    continue

                data = []

                name = row['Company']
                vat_no = row['Vat Number']
                billing_address = row['Billing Address Line1']
                billing_address_alt = row['Billing Address Line2']
                billing_zip = row['Billing Address Zip']
                billing_city = row['Billing Address City']
                billing_country = row['Billing Address Country']

                for column in twinfield_colums:
                    if column == 'code':
                        code = self.get_code(tenant.id)
                        data.append(code)
                    elif column == 'name':
                        data.append(name)
                    elif column == 'defaultaddress':
                        # Constant value.
                        data.append('TRUE')
                    elif column == 'addresstype':
                        # Constant value.
                        data.append('invoice')
                    elif column == 'Companyname':
                        # Yes this is intentional.
                        data.append(name)
                    elif column == 'addressline1':
                        data.append(billing_address)
                    elif column == 'addressline2':
                        data.append(billing_address_alt)
                    elif column == 'postcode':
                        data.append(billing_zip)
                    elif column == 'City':
                        data.append(billing_city)
                    elif column == 'country':
                        data.append(billing_country)
                    elif column == 'VATno':
                        data.append(vat_no)
                    elif column == 'duedays':
                        data.append(30)
                    elif column == 'ebilling':
                        data.append('FALSE')
                    elif column == 'generalledgeraccount':
                        data.append(1300)
                    else:
                        # Rest won't be filled in.
                        data.append('')

                writer.writerow(data)

                gc.collect()

        with default_storage.open('twinfield_invoices.csv', 'wb') as csvfile:
            invoices = BillingInvoice.objects.all().values_list('invoice_id', flat=True)

            # Not all columns have to be filled in, but Twinfield does require all columns to be present.
            twinfield_colums = [
                'invcode', 'AR number', 'Group', 'invoice date', 'due date', 'header', 'footer', 'currency',
                'quantity', 'article', 'subarticle', 'description', 'article price(vatexclusive)',
                'article price(vatinclusive)', 'VAT', 'GL Account', 'Free text field 1', 'Free text field 2',
                'Free text field 3', 'goods/services', 'uitvoeringsdatum'
            ]

            eu_countries = [
                'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU',
                'MT', 'NL', 'AT', 'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE', 'UK'
            ]

            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(twinfield_colums)

            rows = []

            for row in self.read_csvfile('Invoices.csv'):
                # TODO Fetch all customers.
                customer_id = row['Customer Id']

                if not customer_id:
                    continue

                try:
                    tenant = Tenant.objects.get(billing__customer_id=customer_id)
                except Tenant.DoesNotExist:
                    continue

                # Not paid yet, so no reason to process it.
                if row['Status'] == 'Pending':
                    continue

                data = []

                invoice_number = int(row['Invoice Number'])

                # Skip invoices which have been processed or are in the draft stage.
                if invoice_number in invoices:
                    continue

                invoice_date = row['Invoice Date']

                invoice_date = datetime.strptime(invoice_date, '%d-%b-%Y %H:%M').strftime('%d/%m/%Y')

                amount = row['Amount']
                tax_total = row['Tax Total']
                billing_country_code = row['Customer Billing Country']

                if billing_country_code == 'NL':
                    tax_type = 'VH'
                    article = 1
                elif billing_country_code in eu_countries:
                    tax_type = 'ICP'
                    article = 2
                else:
                    tax_type = 'VN'
                    article = 3

                for column in twinfield_colums:
                    if column == 'invcode':
                        # Constant value.
                        data.append('FACTUUR')
                    elif column == 'AR number':
                        code = self.get_code(tenant.id)
                        data.append(code)
                    elif column == 'invoice date':
                        data.append(invoice_date)
                    elif column == 'quantity':
                        # Constant value.
                        data.append(1)
                    elif column == 'article':
                        data.append(article)
                    elif column == 'article price(vatexclusive)':
                        tax_exclusive_amount = Decimal(amount) - Decimal(tax_total)
                        data.append(tax_exclusive_amount)
                    elif column == 'VAT':
                        data.append(tax_type)
                    elif column == 'goods/services':
                        if tax_type == 'ICP':
                            data.append('services')
                        else:
                            data.append('')
                    elif column == 'uitvoeringsdatum':
                        if tax_type == 'ICP':
                            data.append(invoice_date)
                        else:
                            data.append('')
                    else:
                        # Rest won't be filled in.
                        data.append('')

                rows.append(data)

                BillingInvoice.objects.create(invoice_id=invoice_number)

            # Sort the rows by the code we generated based on the tenant ID.
            rows = sorted(rows, key=operator.itemgetter(1), reverse=True)
            writer.writerows(rows)
            gc.collect()

    def read_csvfile(self, file_name):
        """
        Read from path assuming it's a file with ',' separated values.
        """
        # Newlines are breaking correct csv parsing. Write correct temporary file to parse.
        csv_file = default_storage.open(file_name, 'rU')
        reader = csv.DictReader(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
        for row in reversed(list(reader)):
            yield row
