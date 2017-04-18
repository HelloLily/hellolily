# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_users_to_account_admin(apps, schema_editor):
    LilyUser = apps.get_model('users', 'LilyUser')
    Tenant = apps.get_model('tenant', 'Tenant')
    Group = apps.get_model('auth', 'Group')
    account_admin = Group.objects.get_or_create(name='account_admin')[0]

    for tenant in Tenant.objects.all():
        users = LilyUser.objects.filter(tenant=tenant)
        first_user = users.order_by('date_joined').first()

        if first_user:
            first_user.groups.add(account_admin)

    for superuser in LilyUser.objects.filter(is_superuser=True):
        superuser.groups.add(account_admin)

def remove_users_from_account_admin(apps, schema_editor):
    LilyUser = apps.get_model('users', 'LilyUser')
    Tenant = apps.get_model('tenant', 'Tenant')
    Group = apps.get_model('auth', 'Group')
    account_admin = Group.objects.get(name='account_admin')

    for tenant in Tenant.objects.all():
        users = LilyUser.objects.filter(tenant=tenant)
        first_user = users.order_by('date_joined').first()

        if first_user:
            if first_user.groups.filter(name='account_admin').exists():
                first_user.groups.remove(account_admin)

    for superuser in LilyUser.objects.filter(is_superuser=True):
        superuser.groups.remove(account_admin)

    account_admin.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_set_user_info'),
        ('tenant', '0004_tenant_currency'),
    ]

    operations = [
        migrations.RunPython(add_users_to_account_admin, remove_users_from_account_admin),
    ]
