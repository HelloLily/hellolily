from optparse import make_option

from django.core.management.base import BaseCommand

from lily.accounts.factories import AccountFactory
from lily.cases.factories import CaseFactory
from lily.contacts.factories import ContactFactory, function_factory
from lily.deals.factories import DealFactory
from lily.notes.factories import NoteFactory
from lily.tenant.factories import TenantFactory
from lily.tenant.models import Tenant
from lily.users.factories import AdminCustomUserFactory, CustomUserFactory


class Command(BaseCommand):
    help = """Populate the database with test data. It will create a new tenant, \
or use an existent tenant if passed as an argument."""

    option_list = BaseCommand.option_list + (
        make_option('-t', '--target',
                    action='store',
                    dest='target',
                    default='all',
                    help='Choose specific comma separated targets, see the code for a list.',
                    ),
        make_option('-b', '--batch-size',
                    action='store',
                    dest='batch_size',
                    default='5',
                    help='Override the batch size.',
                    ),
        make_option('--tenant',
                    action='store',
                    dest='tenant',
                    default='',
                    help='Specify a tenant to create the testdata in, or leave blank to create new.',
                    ),
    )

    def handle(self, *args, **options):
        batch_size = int(options['batch_size'])
        targets = options['target']
        tenantOption = options['tenant'].strip()
        if not tenantOption:
            tenant = TenantFactory()
        else:
            tenant = Tenant.objects.get(pk=int(tenantOption))

        for target in targets.split(','):
            getattr(self, target)(batch_size, tenant)
        self.stdout.write('Done running "%s" with batch size %s in %s.' % (targets,
                                                                           batch_size,
                                                                           tenant))

    def all(self, size, tenant):
        # Call every target.
        self.users(size, tenant)
        self.contacts_and_accounts(size, tenant)
        self.deals(size, tenant)
        self.cases(size, tenant)
        self.deals(size, tenant)
        self.notes(size, tenant)
        # create admin user last
        self.admin(size, tenant)

    def notes(self, size, tenant):
        NoteFactory.create_batch(size, tenant=tenant)
        # create multiple notes for single subject and multi author
        NoteFactory.create_batch(size, tenant=tenant,
                                 subject=AccountFactory(tenant=tenant))
        # create multiple notes for single subject and single author
        NoteFactory.create_batch(size, tenant=tenant,
                                 author=CustomUserFactory(tenant=tenant),
                                 subject=AccountFactory(tenant=tenant))

    def deals(self, size, tenant):
        DealFactory.create_batch(size, tenant=tenant)

    def cases(self, size, tenant):
        CaseFactory.create_batch(size, tenant=tenant)

    def admin(self, size, tenant):
        admin = AdminCustomUserFactory(tenant=tenant)
        self.stdout.write('You can login with:\n%s\n%s' % (admin.contact.email_addresses.first(),
                                                           admin.password_raw))

    def users(self, size, tenant):
        CustomUserFactory.create_batch(size, tenant=tenant)

    def contacts_and_accounts(self, size, tenant):
        # create various contacts
        ContactFactory.create_batch(size, tenant=tenant)
        # create accounts with zero contact
        AccountFactory.create_batch(size, tenant=tenant)
        # create account with multi contacts
        function_factory(tenant).create_batch(size, account=AccountFactory(tenant=tenant))
