# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import chargebee
from django.conf import settings
from django.db import migrations, models

# Mock commit to trigger migrations again tonight since the previous migration failed.

def create_billing_objects(apps, schema_editor):
    Billing = apps.get_model('billing', 'Billing')
    Plan = apps.get_model('billing', 'Plan')
    Tenant = apps.get_model('tenant', 'Tenant')
    Group = apps.get_model('auth', 'Group')

    plans = Plan.objects.all()
    plan_id = settings.CHARGEBEE_PRO_TRIAL_PLAN_NAME

    for tenant in Tenant.objects.all():
        tenant_users = tenant.lilyuser_set

        tenant.billing = Billing.objects.create()

        # Get the tenant admin (or first one in case of multiple).
        admin_user = tenant_users.filter(groups__name='account_admin').first()

        if not admin_user:
            admin_user = tenant_users.first()
            account_admin_group = Group.objects.get_or_create(name='account_admin')[0]
            admin_user.groups.add(account_admin_group)
            admin_user.save()

        if admin_user:
            result = chargebee.Subscription.create({
                'plan_id': plan_id,
                'plan_quantity': tenant_users.count(),
                'customer': {
                    'first_name': admin_user.first_name,
                    'last_name': admin_user.last_name,
                    'email': admin_user.email,
                    'company': tenant.name,
                },
            })

            tenant.billing.customer_id = result.customer.id
            tenant.billing.subscription_id = result.subscription.id
            tenant.billing.plan = plans.get(name=plan_id)
            tenant.billing.trial_started = True
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
