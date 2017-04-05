# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import chargebee
from django.conf import settings
from django.db import migrations, models


def create_billing_objects(apps, schema_editor):
    Billing = apps.get_model('billing', 'Billing')
    Tenant = apps.get_model('tenant', 'Tenant')

    chargebee.configure(settings.CHARGEBEE_API_KEY, settings.CHARGEBEE_SITE)

    for tenant in Tenant.objects.all():
        tenant.billing = Billing.objects.create()

        # Get the tenant admin (or first one in case of multiple).
        admin_user = tenant.lilyuser_set.filter(groups__name='account_admin').first()

        if admin_user:
            result = chargebee.Customer.create({
                'first_name': admin_user.first_name,
                'last_name': admin_user.last_name,
                'email': admin_user.email,
                'company': tenant.name,
            })

        tenant.save()

def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0005_tenant_billing'),
    ]

    operations = [
        migrations.RunPython(create_billing_objects, do_nothing),
    ]
