from optparse import make_option

from django.core.management.base import BaseCommand

from lily.accounts.factories import AccountFactory
from lily.cases.factories import CaseFactory
from lily.contacts.factories import ContactFactory, function_factory
from lily.deals.factories import DealFactory
from lily.notes.factories import NoteFactory
from lily.tenant.factories import TenantFactory
from lily.tenant.models import Tenant
from lily.users.factories import LilySuperUserFactory, LilyUserFactory


class Command(BaseCommand):
    help = """Populate the database with test data. It will create a new tenant, \
or use an existent tenant if passed as an argument."""

    # please keep in sync with methods defined below
    target_choices = ['all', 'contacts_and_accounts', 'cases', 'deals', 'notes', 'users', 'superusers', ]

    option_list = BaseCommand.option_list + (
        make_option('-t', '--target',
                    action='store',
                    dest='target',
                    default='all',
                    help='Choose specific comma separated targets, choose from %s' % target_choices,
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
        self.stdout.write('Done running "%s" with batch size %s in %s.' % (
            targets,
            batch_size,
            tenant
        ))

    def all(self, size, tenant):
        # Call every target.
        self.contacts_and_accounts(size, tenant)
        self.cases(size, tenant)
        self.deals(size, tenant)
        self.notes(size, tenant)
        self.users(size, tenant)
        self.superusers(size, tenant)

    def contacts_and_accounts(self, size, tenant):
        # create various contacts
        ContactFactory.create_batch(size, tenant=tenant)
        # create accounts with zero contact
        AccountFactory.create_batch(size, tenant=tenant)
        # create account with multi contacts
        function_factory(tenant).create_batch(size, account=AccountFactory(tenant=tenant))
        # create account with assigned_to
        function_factory(tenant).create_batch(
            size,
            account=AccountFactory(tenant=tenant,
                                   assigned_to=LilyUserFactory(tenant=tenant))
        )

    def cases(self, size, tenant):
        CaseFactory.create_batch(size, tenant=tenant)

    def deals(self, size, tenant):
        DealFactory.create_batch(size, tenant=tenant)

    def notes(self, size, tenant):
        NoteFactory.create_batch(size, tenant=tenant)
        # create multiple notes for single subject and multi author
        NoteFactory.create_batch(size, tenant=tenant, subject=AccountFactory(tenant=tenant))
        # create multiple notes for single subject and single author
        NoteFactory.create_batch(
            size,
            tenant=tenant,
            author=LilyUserFactory(tenant=tenant),
            subject=AccountFactory(tenant=tenant)
        )

    def users(self, size, tenant):
        LilyUserFactory.create_batch(size, tenant=tenant)
        user = LilyUserFactory.create(tenant=tenant, is_active=True)
        self.stdout.write('You can now login as a normal user in %(tenant)s with:\n%(email)s\n%(password)s\n' % {
            'tenant': tenant,
            'email': user.email,
            'password': 'lilyuser'
        })

    def superusers(self, size, tenant):
        LilySuperUserFactory.create_batch(size, tenant=tenant)
        user = LilySuperUserFactory.create(tenant=tenant, is_active=True)
        self.stdout.write('\nYou can now login as a superuser in %(tenant)s with:\n%(email)s\n%(password)s\n\n' % {
            'tenant': tenant,
            'email': user.email,
            'password': 'lilysuperuser'
        })

