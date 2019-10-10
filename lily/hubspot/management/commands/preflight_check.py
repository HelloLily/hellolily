import sys

from django.core.management.base import BaseCommand

from lily.accounts.models import AccountStatus, Account
from lily.cases.models import CaseStatus, CaseType
from lily.hubspot.utils import get_mappings, get_accounts_without_website, get_contacts_without_email_address, \
    get_accounts_with_non_unique_websites, get_contacts_with_non_unique_email_addresses
from lily.tags.models import Tag
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


# number of non unique websites: 244
# number of accounts without a website: 20521
# number of non unique email addresses: 2557
# number of contacts without an email address: 2484


# number of non unique websites: d
# number of accounts without a website: 20521
# number of contacts without an email address: 4358


def run_all_checks(tenant_id):
    m = get_mappings(tenant_id)
    all_checks = (
        # Mappings.
        check_lilyuser_to_owner_mapping(tenant_id, m),
        check_account_status_to_company_type_mapping(tenant_id, m),
        check_case_status_to_ticket_status_mapping(tenant_id, m),
        check_case_type_to_ticket_category_mapping(tenant_id, m),

        # Account checks.
        check_accounts_with_non_unique_websites(tenant_id),
        check_accounts_without_a_website(tenant_id),
        check_accounts_with_cold_email_tag(tenant_id),

        # Contact checks.
        check_contacts_with_non_unique_email_addresses(tenant_id),
        check_contacts_without_an_email_address(tenant_id),
    )

    return all(all_checks)


def check_lilyuser_to_owner_mapping(tenant_id, m):
    users = set(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).values_list('pk', flat=True))
    mappings = set(m.lilyuser_to_owner_mapping.keys())

    missing_user_mappings = users.difference(mappings)

    if missing_user_mappings:
        print('number of missing user mappings: {}'.format(len(missing_user_mappings)))
        return False

    return True


def check_case_status_to_ticket_status_mapping(tenant_id, m):
    statusses = set(CaseStatus.objects.filter(tenant_id=tenant_id).values_list('pk', flat=True))
    mappings = set(m.case_status_to_ticket_stage_mapping.keys())

    missing_status_mappings = statusses.difference(mappings)

    if missing_status_mappings:
        print('number of missing case status mappings: {}'.format(len(missing_status_mappings)))
        return False

    return True


def check_case_type_to_ticket_category_mapping(tenant_id, m):
    types = set(CaseType.objects.filter(tenant_id=tenant_id).values_list('pk', flat=True))
    mappings = set(m.case_type_to_ticket_category_mapping.keys())

    missing_type_mappings = types.difference(mappings)

    if missing_type_mappings:
        print('number of missing case type mappings: {}'.format(len(missing_type_mappings)))
        return False

    return True


def check_account_status_to_company_type_mapping(tenant_id, m):
    statuses = set(AccountStatus.objects.filter(tenant_id=tenant_id).values_list('pk', flat=True))
    mappings = set(m.account_status_to_company_type_mapping.keys())

    missing_user_mappings = statuses.difference(mappings)

    if missing_user_mappings:
        print('number of missing account status mappings: {}'.format(len(missing_user_mappings)))
        return False

    return True


def check_accounts_with_non_unique_websites(tenant_id):
    results = get_accounts_with_non_unique_websites(tenant_id)

    if results:
        print('number of non unique websites: {}'.format(len(results)))
        return False

    return True


def check_accounts_without_a_website(tenant_id):
    results = get_accounts_without_website(tenant_id)

    if results:
        print('number of accounts without a website: {}'.format(len(results)))
        return False

    return True


def check_accounts_with_cold_email_tag(tenant_id):
    account_content_type = Account().content_type
    account_ids = Tag.objects.filter(
        tenant_id=tenant_id,
        name='cold email',
        content_type=account_content_type
    ).values_list('object_id', flat=True)
    account_list = Account.objects.filter(id__in=account_ids, is_deleted=False, tenant_id=tenant_id)

    if account_list:
        print('number of accounts with cold email tag: {}'.format(len(account_list)))
        print([acc.pk for acc in account_list])
        return False

    return True


def check_contacts_with_non_unique_email_addresses(tenant_id):
    results = get_contacts_with_non_unique_email_addresses(tenant_id)

    if results:
        print('number of non unique email addresses: {}'.format(len(results)))
        return False

    return True


def check_contacts_without_an_email_address(tenant_id):
    results = get_contacts_without_email_address(tenant_id)

    if results:
        print('number of contacts without an email address: {}'.format(len(results)))
        return False

    return True


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Running preflight checks. \n\n')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())

        success = run_all_checks(tenant_id)
        self.stdout.write(self.style.SUCCESS('>>') + '  Preflight checks finished, issues found: {}. \n\n'.format(
            not success
        ))

        sys.exit(0 if success else 1)
