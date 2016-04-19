# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


# Mapping statuses from the old to new one.
status_mapping = {
    'inactive': 'Relation',
    'active': 'Active',
    'pending': 'Prospect',
    'prev_customer': 'Previous customer',
    'bankrupt': 'Previous customer',
    'unknown': 'Relation',
}


def fix_empty_status(apps, schema_editor):
    Deal = apps.get_model('deals', 'Deal')
    DealStatus = apps.get_model('deals', 'DealStatus')
    Account = apps.get_model('accounts', 'Account')

    accounts = Account.objects.filter(status='')

    for account in accounts:
        account.update_modified = False

        if account.customer_id != '':
            account.status = 'active'
        else:
            deals = Deal.objects.filter(account=account)
            deal_status_won = DealStatus.objects.get(name='Won', tenant=account.tenant)
            deals_won = Deal.objects.filter(account=account, status=deal_status_won)
            if not deals:
                account.status = 'inactive'  # Is mapped to Relation after link_status_entries.
            else:
                if deals_won:
                    account.status = 'active'
                else:
                    # Account has deals, but no deals won.
                    account.status = 'pending'  # Is mapped to Prospect after link_status_entries.

        account.save()


def create_status_entries(apps, schema_editor):
    status_choices_new = set(status_mapping.values())  # Get unique new statuses.

    AccountStatus = apps.get_model('accounts', 'AccountStatus')
    Tenant = apps.get_model('tenant', 'Tenant')

    for tenant in Tenant.objects.all():
        for status_choice in status_choices_new:
            AccountStatus.objects.create(name=status_choice, tenant=tenant)


def link_status_entries(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')
    AccountStatus = apps.get_model('accounts', 'AccountStatus')

    accounts = Account.objects.all()

    for account in accounts:
        account.update_modified = False
        status_object = AccountStatus.objects.get(name=status_mapping[account.status], tenant=account.tenant)
        account.status_id = status_object.id
        account.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_account_status_prepare'),
        ('deals', '0027_auto_20160408_1519'),
    ]

    operations = [
        migrations.RunPython(fix_empty_status),
        migrations.RunPython(create_status_entries),
        migrations.RunPython(link_status_entries),
    ]
