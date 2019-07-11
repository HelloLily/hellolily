import sys

from django.core.management.base import BaseCommand
from django.db import connection

from lily.accounts.models import AccountStatus, Account
from lily.hubspot.mappings import lilyuser_to_owner_mapping, account_status_to_company_type_mapping
from lily.hubspot.utils import get_accounts_without_website, get_contacts_without_email_address
from lily.tags.models import Tag
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


def run_all_checks(tenant_id):
    all_checks = (
        # Mappings.
        # check_lilyuser_to_owner_mapping(tenant_id),
        check_account_status_to_company_type_mapping(tenant_id),

        # Account checks.
        check_accounts_with_non_unique_websites(tenant_id),
        check_accounts_without_a_website(tenant_id),
        check_accounts_with_cold_email_tag(tenant_id),

        # Contact checks.
        check_contacts_with_non_unique_email_addresses(tenant_id),
        check_contacts_without_an_email_address(tenant_id),
    )

    return all(all_checks)


def check_lilyuser_to_owner_mapping(tenant_id):
    users = set(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).values_list('pk', flat=True))
    mappings = set(lilyuser_to_owner_mapping.keys())

    missing_user_mappings = users.difference(mappings)

    if missing_user_mappings:
        print('number of missing user mappings: {}'.format(len(missing_user_mappings)))
        return False

    return True


def check_account_status_to_company_type_mapping(tenant_id):
    statuses = set(AccountStatus.objects.filter(tenant_id=tenant_id).values_list('pk', flat=True))
    mappings = set(account_status_to_company_type_mapping.keys())

    missing_user_mappings = statuses.difference(mappings)

    if missing_user_mappings:
        print('number of missing account status mappings: {}'.format(len(missing_user_mappings)))
        return False

    return True


def check_accounts_with_non_unique_websites(tenant_id):
    sql_query = '''
        SELECT      REGEXP_REPLACE(accounts_website.website, '^https?://(www.)?', '') as "stripped_website",
                    accounts_website.tenant_id,
                    COUNT(1) AS "dcount",
                    ARRAY_AGG(accounts_website.account_id) AS "account ids",
                    ARRAY_AGG(accounts_website.id) AS "website ids"
        FROM        accounts_website
        JOIN        accounts_account
        ON          accounts_website.account_id = accounts_account.id
        WHERE       accounts_website.website != 'http://'
        AND         accounts_website.tenant_id = 10
        AND         accounts_account.is_deleted = FALSE
        GROUP BY    accounts_website.tenant_id,
                    "stripped_website"
        HAVING      COUNT(accounts_website.website) > 1;
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql_query, [tenant_id, ])
        results = cursor.fetchall()

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
    sql_query = '''
        SELECT      utils_emailaddress.email_address,
                    COUNT(utils_emailaddress.email_address) AS "dcount",
                    ARRAY_AGG(contacts_contact_email_addresses.contact_id) AS "contact ids",
                    ARRAY_AGG(utils_emailaddress.id) AS "email ids"
        FROM        utils_emailaddress
        JOIN        contacts_contact_email_addresses
        ON          contacts_contact_email_addresses.emailaddress_id = utils_emailaddress.id
        JOIN        contacts_contact
        ON          contacts_contact_email_addresses.contact_id = contacts_contact.id
        WHERE       utils_emailaddress.tenant_id = %s AND utils_emailaddress.status != 0
        AND         contacts_contact.is_deleted = FALSE
        GROUP BY    utils_emailaddress.tenant_id, utils_emailaddress.email_address
        HAVING      COUNT(utils_emailaddress.email_address) > 1;
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql_query, [tenant_id, ])
        results = cursor.fetchall()

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
