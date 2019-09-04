from bs4 import UnicodeDammit
from django.db import connection

from lily.utils.functions import format_phone_number
from lily.utils.models.models import PhoneNumber


def _u(value):
    return UnicodeDammit(value).unicode_markup


def _s(value):
    return unicode(value).encode('utf-8')


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

    phone_numbers = {pn.type: pn for pn in instance.prefetched_phone_numbers}

    phone = phone_numbers.get('work', PhoneNumber()).number
    mobile = phone_numbers.get('mobile', PhoneNumber()).number

    return {
        'phone': _s(format_phone_number(phone, country, True) if phone else ''),
        'mobile': _s(format_phone_number(mobile, country, True) if mobile else ''),
    }


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
        return cursor.fetchall()


def get_contacts_without_email_address(tenant_id):
    sql_query = '''
        SELECT  id
        FROM    contacts_contact
        WHERE   id NOT IN (
                    SELECT contact_id
                    FROM contacts_contact_email_addresses
                )
        AND     tenant_id = %s
        AND is_deleted = FALSE;
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql_query, [tenant_id, ])
        return cursor.fetchall()
