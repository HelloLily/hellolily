# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import chargebee
from django.db import migrations, models


def create_plan_objects(apps, schema_editor):
    Plan = apps.get_model('billing', 'Plan')
    plans = [
        {'name': 'lily-personal', 'tier': 0},
        {'name': 'lily-team', 'tier': 1},
        {'name': 'lily-professional', 'tier': 2}
    ]

    for plan in plans:
        Plan.objects.create(name=plan.get('name'), tier=plan.get('tier'))


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
        ('tenant', '0005_tenant_billing'),
        ('users', '0021_lilyuser_add_to_account_admin_group'),
    ]

    operations = [
        migrations.RunPython(create_plan_objects, do_nothing),
    ]
