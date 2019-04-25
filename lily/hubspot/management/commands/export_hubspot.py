import StringIO
import csv

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser
from lily.utils.models.models import Address


def _u(value):
    return unicode(value).encode('utf-8')


field_names = (
    # Account.
    'account_id',
    'account_name',
    'account_domain',
    'account_phone',
    'account_address_street',
    'account_address_city',
    'account_address_state',
    'account_address_zip',
    'account_address_country',
    'account_lily_created',
    'account_lily_modified',

    # Contact.
    'contact_id',
    'contact_first_name',
    'contact_last_name',
    'contact_email',
    'contact_phone',
    'contact_address_street',
    'contact_address_city',
    'contact_address_state',
    'contact_address_zip',
    'contact_address_country',
    'contact_lily_created',
    'contact_lily_modified',

    # Deal.
    'deal_id',
    'deal_name',
    'deal_description',

    # Case.
    'case_id',

    # Note.
    # 'note_id',
)


class Command(BaseCommand):
    page_size = 5

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting export. \n'))

        # Configure the tenant for all queries.
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        self.export_accounts(writer)
        self.export_contacts(writer)
        # self.export_deals(writer)
        # self.export_cases(writer)
        # self.export_notes(writer)

        filename = 'exports/tenant_{}/lily_to_hubspot.csv'.format(tenant_id)
        default_storage.save(name=filename, content=csvfile)

        self.stdout.write(self.style.SUCCESS('Finished export.'))
        self.stdout.write('Written to file: {} \n\n'.format(filename))

    def export_accounts(self, writer):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with accounts')
        account_qs = Account.objects.filter(is_deleted=False).order_by('pk')
        paginator = Paginator(account_qs, self.page_size)

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            account_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for account in account_list:
                address = account.addresses.first() or Address()

                data = {
                    'account_id': _u(account.pk),
                    'account_name': _u(account.name),
                    'account_phone': _u(account.phone_number.number if account.phone_number else ''),
                    'account_address_street': _u(address.address),
                    'account_address_city': _u(address.city),
                    'account_address_state': _u(address.state_province),
                    'account_address_zip': _u(address.postal_code),
                    'account_address_country': _u(address.country),
                    'account_lily_created': _u(account.created),
                    'account_lily_modified': _u(account.modified),
                }

                writer.writerow(data)
        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported accounts. \n\n')

    def export_contacts(self, writer):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with contacts')
        contact_qs = Contact.objects.filter(is_deleted=False).order_by('pk')
        paginator = Paginator(contact_qs, self.page_size)

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            contact_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for contact in contact_list:
                address = contact.addresses.first() or Address()
                account_id = contact.accounts.values_list('pk', flat=True).first() or ''

                data = {
                    # To match with the account.
                    'account_id': _u(account_id),

                    # The actual contact information.
                    'contact_id': _u(contact.pk),
                    'contact_first_name': _u(contact.first_name),
                    'contact_last_name': _u(contact.last_name),
                    'contact_email': _u(contact.primary_email or ''),
                    'contact_phone': _u(contact.phone_number.number if contact.phone_number else ''),
                    'contact_address_street': _u(address.address),
                    'contact_address_city': _u(address.city),
                    'contact_address_state': _u(address.state_province),
                    'contact_address_zip': _u(address.postal_code),
                    'contact_address_country': _u(address.country),
                    'contact_lily_created': _u(contact.created),
                    'contact_lily_modified': _u(contact.modified),
                }

                writer.writerow(data)
        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported contacts \n\n')

    def export_deals(self, writer):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with deals')
        deals_qs = Deal.objects.filter(is_deleted=False).order_by('pk')
        paginator = Paginator(deals_qs, self.page_size)

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            deal_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for deal in deal_list:
                data = {
                    # To match with the account and/or contact.
                    'account_id': _u(deal.account_id or ''),
                    'contact_id': _u(deal.contact_id or ''),

                    # The actual contact information.
                    'deal_id': _u(deal.pk),
                    'deal_name': _u(deal.name),
                    'deal_description': _u(deal.description),
                }

                writer.writerow(data)
        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported deals \n\n')

    def export_cases(self, writer):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with cases')
        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported cases \n\n')

    def export_notes(self, writer):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with notes')
        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported notes \n\n')
