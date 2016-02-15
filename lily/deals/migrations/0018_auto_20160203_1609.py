# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


def do_nothing(apps, schema_editor):
    pass


def account_forward(apps, schema_editor):
    Account = apps.get_model("accounts", "Account")
    Deal = apps.get_model("deals", "Deal")
    Tenant = apps.get_model("tenant", "Tenant")

    # Loop through all tenants, because we want to assign an account to the deals per tenant.
    for tenant in Tenant.objects.all():
        # Get or create the 'Unknown' account for this tenant, so we can link it to the deals.
        account, created = Account.objects.get_or_create(
            tenant=tenant,
            name='Unknown',
            defaults={
                'description': 'This account is assigned when the real account is not known.',
            }
        )

        # Update the deals with the 'Unknown' account linked.
        Deal.objects.filter(tenant=tenant, account=None).update(account=account)


def amount_once_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")

    Deal.objects.filter(amount_once=None).update(amount_once=0)


def amount_recurring_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")

    Deal.objects.filter(amount_recurring=None).update(amount_recurring=0)


def contacted_by_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")

    # At the point of this migration 5 means 'other', so this means we assign 'other' as the way we were contacted.
    Deal.objects.filter(contacted_by=None).update(contacted_by=5)


def currency_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")

    # Set the euro as default currency for all deals that have no currency.
    Deal.objects.filter(currency=None).update(currency='EUR')


def found_through_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")

    # At the point of this migration 4 means 'other', so this means we assign 'other' as the way we were found.
    Deal.objects.filter(found_through=None).update(found_through=4)


def next_step_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")
    DealNextStep = apps.get_model("deals", "DealNextStep")
    Tenant = apps.get_model("tenant", "Tenant")

    # Loop through all tenants, because we want to assign a next step to the deals per tenant.
    for tenant in Tenant.objects.all():
        # Get or create the 'None' step for this tenant, so we can link it to the deals.
        next_step, created = DealNextStep.objects.get_or_create(
            tenant=tenant,
            name='None'
        )

        # Update the deals with the 'None' step linked.
        Deal.objects.filter(tenant=tenant, next_step=None).update(next_step=next_step)


def stage_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")

    # At the point of this migration 0 means 'open', so this means we assign 'open' as the current status.
    Deal.objects.filter(stage=None).update(stage=0)


def why_customer_forward(apps, schema_editor):
    Deal = apps.get_model("deals", "Deal")
    DealWhyCustomer = apps.get_model("deals", "DealWhyCustomer")
    Tenant = apps.get_model("tenant", "Tenant")

    # Loop through all tenants, because we want to assign a next step to the deals per tenant.
    for tenant in Tenant.objects.all():
        # Get or create the 'None' step for this tenant, so we can link it to the deals.
        why_customer, created = DealWhyCustomer.objects.get_or_create(
            tenant=tenant,
            name='Unknown'
        )

        # Update the deals with the 'None' step linked.
        Deal.objects.filter(tenant=tenant, why_customer=None).update(why_customer=why_customer)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20150420_1006'),
        ('deals', '0017_auto_20160129_0959'),
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(account_forward, do_nothing),
        migrations.RunPython(amount_once_forward, do_nothing),
        migrations.RunPython(amount_recurring_forward, do_nothing),
        migrations.RunPython(contacted_by_forward, do_nothing),
        migrations.RunPython(currency_forward, do_nothing),
        migrations.RunPython(found_through_forward, do_nothing),
        migrations.RunPython(next_step_forward, do_nothing),
        migrations.RunPython(stage_forward, do_nothing),
        migrations.RunPython(why_customer_forward, do_nothing),
    ]
