import chargebee
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from factory import iterator, Iterator

from lily.accounts.factories import AccountFactory
from lily.billing.models import Plan, Billing
from lily.calls.factories import CallRecordFactory, CallParticipantFactory
from lily.calls.models import CallParticipant
from lily.cases.factories import CaseFactory, CaseTypeFactory, CaseStatusFactory
from lily.contacts.factories import ContactFactory, FunctionFactory
from lily.deals.factories import (DealFactory, DealContactedByFactory, DealFoundThroughFactory, DealNextStepFactory,
                                  DealStatusFactory, DealWhyCustomerFactory)
from lily.notes.factories import NoteFactory
from lily.tenant.factories import TenantFactory
from lily.tenant.models import Tenant
from lily.users.factories import TeamFactory, LilySuperUserFactory, LilyUserFactory


class Command(BaseCommand):
    help = """Populate the database with test data. It will create a new tenant,
or use an existent tenant if passed as an argument."""

    # please keep in sync with methods defined below
    target_choices = [
        'all', 'users_teams', 'users_user', 'contacts_contact', 'accounts_account', 'accounts_function', 'calls_call',
        'cases_case_type', 'cases_case_status', 'cases_case', 'deals_deal_contacted_by', 'deals_deal_found_through',
        'deals_deal_next_step', 'deals_deal_status', 'deals_deal_why_customer', 'deals_deal', 'notes_note',
        'users_login',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '-t', '--target',
            action='store',
            dest='target',
            default='all',
            help='Choose a specific target, options are: %s' % self.target_choices
        )
        parser.add_argument(
            '-b', '--batch-size',
            action='store',
            dest='batch_size',
            default='20',
            help='Override the batch size.'
        )
        parser.add_argument(
            '--tenant',
            action='store',
            dest='tenant',
            default='',
            help='Specify a tenant to create the testdata in, or leave blank to create new.'
        )

    def handle(self, *args, **options):
        self.batch_size = int(options['batch_size'])

        self.target = options['target'].strip()
        if self.target not in self.target_choices:
            raise CommandError(
                'Unknown target specified, please only use one of the following:\n'
                '    %s' % "\n    ".join(self.target_choices)
            )

        tenant_id = options['tenant'].strip()
        if tenant_id:
            self.tenant = Tenant.objects.get(pk=int(tenant_id))
        else:
            self.tenant = TenantFactory()

        getattr(self, self.target)()

        self.stdout.write('Done running "%s" with batch size %s in %s.' % (
            self.target,
            self.batch_size,
            self.tenant
        ))

    def all(self, **kwargs):
        teams = self.users_team()
        users = self.users_user(teams=Iterator(teams))
        logins = self.users_login(teams=Iterator(teams))

        accounts = self.accounts_account(assigned_to=Iterator(users))
        contacts = self.contacts_contact()
        self.accounts_function(
            account=Iterator(accounts[:len(accounts)]),
            contact=Iterator(contacts[:len(contacts)])
        )

        cases = self.cases_case(
            assigned_to=Iterator(users[:len(users) / 2]),  # Only use half the users for coupling.
            teams=Iterator(teams),
            account=Iterator(accounts[:len(accounts) / 2]),  # Only use half the accounts for coupling.
            contact=Iterator(contacts[:len(contacts) / 2])  # Only use half the contacts for coupling.
        )
        deals = self.deals_deal(
            assigned_to=Iterator(users[:len(users) / 2]),  # Only use half the users for coupling.
            account=Iterator(accounts[:len(accounts) / 2]),  # Only use half the accounts for coupling.
            contact=Iterator(contacts[:len(contacts) / 2])  # Only use half the contacts for coupling.
        )

        # Only use half of the user list and the usable users as authors.
        authors = users[:len(users) / 2] + logins
        subjects = Iterator(
            accounts[:len(accounts) / 4] +
            contacts[:len(contacts) / 4] +
            cases[:len(cases) / 4] +
            deals[:len(deals) / 4]
        )
        self.notes_note(
            author=Iterator(authors),
            subject=subjects
        )

        user_participants = []
        login_participants = []
        account_participants = []

        for user in logins:
            full_name = u' '.join((user.first_name, user.last_name)).encode('utf-8').strip()
            participant = CallParticipant.objects.create(
                name=full_name,
                number=user.phone_number,
                internal_number=user.internal_number,
                tenant=self.tenant
            )
            login_participants.append(participant)

        for user in users:
            full_name = u' '.join((user.first_name, user.last_name)).encode('utf-8').strip()
            participant = CallParticipant.objects.create(
                name=full_name,
                number=user.phone_number,
                internal_number=user.internal_number,
                tenant=self.tenant
            )
            user_participants.append(participant)

        for account in accounts:
            if account.phone_numbers:
                participant = CallParticipant.objects.create(
                    name=account.name,
                    number=account.phone_numbers.all()[0].number,
                    tenant=self.tenant
                )
                account_participants.append(participant)

        # Create callers and destinations lists so that when used as iterators for call record creation,
        # every account calls every user and login, every user calls every account and login etc.
        callers = 2 * account_participants + 2 * login_participants + 2 * user_participants
        destinations = login_participants + user_participants + account_participants + user_participants \
            + account_participants + login_participants

        self.calls_callrecord(
            caller=Iterator(callers),
            destination=Iterator(destinations),
        )

        account_admin_group = Group.objects.get_or_create(name='account_admin')[0]
        # Set the first super user as account admin.
        admin_user = self.tenant.lilyuser_set.filter(is_superuser=True).first()
        admin_user.groups.add(account_admin_group)

        if settings.BILLING_ENABLED:
            plan, created = Plan.objects.get_or_create(name=settings.CHARGEBEE_FREE_PLAN_NAME, tier=0)

            result = chargebee.Subscription.create({
                'plan_id': settings.CHARGEBEE_FREE_PLAN_NAME,
                'customer': {
                    'first_name': admin_user.first_name,
                    'last_name': admin_user.last_name,
                    'email': admin_user.email,
                    'company': self.tenant.name,
                },
            })

            self.tenant.billing = Billing.objects.create(
                customer_id=result.customer.id,
                subscription_id=result.subscription.id,
                plan=plan
            )

        self.tenant.save()

        # Email templates
        # Email template variables

    def users_team(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant)
        })
        teams = TeamFactory.create_batch(**kwargs)

        self.stdout.write('Done with users_team.')

        return teams

    def users_user(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size) / 2,
            'tenant': kwargs.get('tenant', self.tenant),
            'teams': kwargs.get('teams') if kwargs.get('teams') else iterator(self.users_team)
        })

        users = LilyUserFactory.create_batch(**kwargs)
        superusers = LilySuperUserFactory.create_batch(**kwargs)

        self.stdout.write('Done with users_user.')

        return users + superusers

    def users_login(self, **kwargs):
        kwargs.update({
            'tenant': kwargs.get('tenant', self.tenant),
            'teams': kwargs.get('teams') if kwargs.get('teams') else iterator(self.users_team),
            'is_active': kwargs.get('is_active', True),
            'email': 'user%s@lily.com' % self.tenant.pk,
        })

        user = LilyUserFactory.create(**kwargs)

        self.stdout.write('\nYou can now login as a normal user in %(tenant)s with:\n%(email)s\n%(password)s\n' % {
            'tenant': self.tenant,
            'email': user.email,
            'password': 'admin'
        })

        kwargs['email'] = 'superuser%s@lily.com' % self.tenant.pk
        superuser = LilySuperUserFactory.create(**kwargs)

        self.stdout.write('\nYou can now login as a superuser in %(tenant)s with:\n%(email)s\n%(password)s\n\n' % {
            'tenant': self.tenant,
            'email': superuser.email,
            'password': 'admin'
        })

        return [user, superuser]

    def contacts_contact(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        contacts = ContactFactory.create_batch(**kwargs)

        self.stdout.write('Done with contacts_contact.')

        return contacts

    def accounts_account(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size) / 2,
            'tenant': kwargs.get('tenant', self.tenant),
            'assigned_to': kwargs.get('assigned_to') if kwargs.get('assigned_to') else iterator(self.users_user),
        })
        accounts_with_users = AccountFactory.create_batch(**kwargs)

        del kwargs['assigned_to']
        accounts_without_users = AccountFactory.create_batch(**kwargs)

        self.stdout.write('Done with accounts_account.')

        return accounts_with_users + accounts_without_users

    def accounts_function(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size) / 2,
            'account': kwargs.get('account') if kwargs.get('account') else iterator(self.accounts_account),
            'contact': kwargs.get('contact') if kwargs.get('contact') else iterator(self.contacts_contact),
        })
        functions = FunctionFactory.create_batch(**kwargs)

        self.stdout.write('Done with accounts_function.')

        return functions

    def cases_case_type(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        case_types = CaseTypeFactory.create_batch(**kwargs)

        self.stdout.write('Done with cases_case_type.')

        return case_types

    def cases_case_status(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        case_statuses = CaseStatusFactory.create_batch(**kwargs)

        self.stdout.write('Done with cases_case_status.')

        return case_statuses

    def cases_case(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size) / 3,
            'tenant': kwargs.get('tenant', self.tenant),
            'status': kwargs.get('status') if kwargs.get('status') else iterator(self.cases_case_status),
            'type': kwargs.get('type') if kwargs.get('type') else iterator(self.cases_case_type),
            'assigned_to': kwargs.get('assigned_to') if kwargs.get('assigned_to') else iterator(self.users_user),
            'teams': kwargs.get('teams') if kwargs.get('teams') else iterator(self.users_team),
            'account': kwargs.get('account') if kwargs.get('account') else iterator(self.accounts_account),
            'contact': kwargs.get('contact') if kwargs.get('contact') else iterator(self.contacts_contact),
        })

        contact = kwargs.pop('contact')  # Remove contact for now.
        cases_with_account = CaseFactory.create_batch(**kwargs)

        kwargs['account'] = None  # Replace account with contact.
        kwargs['contact'] = contact
        cases_with_contact = CaseFactory.create_batch(**kwargs)

        kwargs['teams'] = None  # Remove all connections.
        kwargs['contact'] = None
        cases_without = CaseFactory.create_batch(**kwargs)

        self.stdout.write('Done with cases_case.')

        return cases_with_account + cases_with_contact + cases_without

    def deals_deal_contacted_by(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        deal_contacted_bys = DealContactedByFactory.create_batch(**kwargs)

        self.stdout.write('Done with deals_deal_contacted_by.')

        return deal_contacted_bys

    def deals_deal_found_through(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        deal_found_throughs = DealFoundThroughFactory.create_batch(**kwargs)

        self.stdout.write('Done with deals_deal_found_throughs.')

        return deal_found_throughs

    def deals_deal_next_step(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        deal_next_steps = DealNextStepFactory.create_batch(**kwargs)

        self.stdout.write('Done with deals_deal_next_steps.')

        return deal_next_steps

    def deals_deal_status(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        deal_statuses = DealStatusFactory.create_batch(**kwargs)

        self.stdout.write('Done with deals_deal_status.')

        return deal_statuses

    def deals_deal_why_customer(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', 5),
            'tenant': kwargs.get('tenant', self.tenant),
        })
        deal_why_customers = DealWhyCustomerFactory.create_batch(**kwargs)

        self.stdout.write('Done with deals_deal_why_customers.')

        return deal_why_customers

    def deals_deal(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size) / 2,
            'tenant': kwargs.get('tenant', self.tenant),
            'account': kwargs.get('account') if kwargs.get('account') else iterator(self.accounts_account),
            'contact': kwargs.get('contact') if kwargs.get('contact') else iterator(self.contacts_contact),
            'assigned_to': kwargs.get('assigned_to') if kwargs.get('assigned_to') else iterator(self.users_user),
            'contacted_by': kwargs.get('contacted_by') if kwargs.get('contacted_by') else
            iterator(self.deals_deal_contacted_by),
            'found_through': kwargs.get('found_through') if kwargs.get('found_through') else
            iterator(self.deals_deal_found_through),
            'next_step': kwargs.get('next_step') if kwargs.get('next_step') else
            iterator(self.deals_deal_next_step),
            'status': kwargs.get('status') if kwargs.get('status') else iterator(self.deals_deal_status),
            'why_customer': kwargs.get('why_customer') if kwargs.get('why_customer') else
            iterator(self.deals_deal_why_customer),
        })
        contact = kwargs.pop('contact')
        kwargs['contact'] = None
        deals_with_accounts = DealFactory.create_batch(**kwargs)

        kwargs['contact'] = contact
        deals_with_contacts = DealFactory.create_batch(**kwargs)

        self.stdout.write('Done with deals_deal.')

        return deals_with_accounts + deals_with_contacts

    def _notes_subject(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size) / 8,  # Only half the amount of subjects for the batch size.
            'tenant': kwargs.get('tenant', self.tenant),
        })

        accounts = self.accounts_account(**kwargs)
        contacts = self.contacts_contact(**kwargs)
        deals = self.deals_deal(**kwargs)
        cases = self.cases_case(**kwargs)

        return accounts + contacts + deals + cases

    def notes_note(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size),
            'tenant': kwargs.get('tenant', self.tenant),
            'author': kwargs.get('author') if kwargs.get('author') else iterator(self.users_user),
            'subject': kwargs.get('subject') if kwargs.get('subject') else iterator(self._notes_subject),
        })

        self.stdout.write('Done with notes_note.')

        return NoteFactory.create_batch(**kwargs)

    def calls_participant(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size),
            'tenant': kwargs.get('tenant', self.tenant),
            'number': kwargs.get('number'),
        })

        return CallParticipantFactory.create_batch(**kwargs)

    def calls_callrecord(self, **kwargs):
        kwargs.update({
            'size': kwargs.get('size', self.batch_size),
            'tenant': kwargs.get('tenant', self.tenant),
            'caller': kwargs.get('caller'),
            'destination': kwargs.get('destination'),
        })

        self.stdout.write('Done with calls_callrecord.')

        return CallRecordFactory.create_batch(**kwargs)
