# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import chargebee
from django.db import migrations, models


def create_billing_objects(apps, schema_editor):
    Billing = apps.get_model('billing', 'Billing')
    Plan = apps.get_model('billing', 'Plan')
    Tenant = apps.get_model('tenant', 'Tenant')

    plans = Plan.objects.all()

    for tenant in Tenant.objects.all():
        tenant.billing = Billing.objects.create()

        # Get the tenant admin (or first one in case of multiple).
        admin_user = tenant.lilyuser_set.filter(groups__name='account_admin').first()

        if not admin_user:
            admin_user = tenant.lilyuser_set.first()

        if admin_user:
            result = chargebee.Subscription.create({
                'plan_id': 'lily-personal',
                'customer': {
                    'first_name': admin_user.first_name,
                    'last_name': admin_user.last_name,
                    'email': admin_user.email,
                    'company': tenant.name,
                },
            })

            tenant.billing.customer_id = result.customer.id
            tenant.billing.subscription_id = result.subscription.id
            tenant.billing.plan = plans.get(name='lily-personal')
            tenant.billing.save()

        tenant.save()

def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_create_plan_objects'),
    ]

    operations = [
        migrations.RunPython(create_billing_objects, do_nothing),
    ]
