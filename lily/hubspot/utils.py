from bs4 import UnicodeDammit
from django.db import connection


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
