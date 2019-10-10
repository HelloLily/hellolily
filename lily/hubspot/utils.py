from importlib import import_module

from bs4 import UnicodeDammit
from django.db import connection

from lily.utils.functions import format_phone_number


def _u(value):
    return UnicodeDammit(value).unicode_markup


def _s(value):
    return unicode(value).encode('utf-8')


def get_mappings(tenant_id):
    return import_module('lily.hubspot.tenant_mappings.tenant_{}'.format(tenant_id))


def _strip_website(website):
    if website.startswith('http://'):
        website = website[7:]

    if website.startswith('https://'):
        website = website[8:]

    if website.startswith('www.'):
        website = website[4:]

    return website


def get_phone_numbers(instance, tenant):
    # Function to retrieve formatted phone numbers from an instance.
    # Requires the Addresses and Phone_numbers to be prefetched.
    country = tenant.country or None
    if instance.prefetched_addresses:
        country = instance.prefetched_addresses[0].country

    phone_number_list = []
    for pn in instance.prefetched_phone_numbers:
        phone_number_list.append(_s(format_phone_number(pn.number, country, True)))

    return ' '.join(phone_number_list)


def get_accounts_with_non_unique_websites(tenant_id):
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
        AND         accounts_website.tenant_id = %s
        AND         accounts_account.is_deleted = FALSE
        GROUP BY    accounts_website.tenant_id,
                    "stripped_website"
        HAVING      COUNT(accounts_website.website) > 1;
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql_query, [tenant_id, ])
        results = cursor.fetchall()

    return results


def get_accounts_without_website(tenant_id):
    sql_query = '''
        SELECT      id
        FROM        accounts_account
        WHERE       id NOT IN (
                        SELECT account_id
                        FROM accounts_website
                        WHERE website NOT IN ('https://', 'http://', '')
                    )
                    AND tenant_id = %s
                    AND is_deleted = FALSE
        ORDER BY    id;
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql_query, [tenant_id, ])
        results = cursor.fetchall()

    return results


def get_contacts_with_non_unique_email_addresses(tenant_id):
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

    return results


def get_contacts_without_email_address(tenant_id):
    sql_query = '''
        SELECT  id
        FROM    contacts_contact
        WHERE   id NOT IN (
                    SELECT contact_id
                    FROM contacts_contact_email_addresses
                )
        AND     tenant_id = %s
        AND     is_deleted = FALSE;
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql_query, [tenant_id, ])
        results = cursor.fetchall()

    return results
