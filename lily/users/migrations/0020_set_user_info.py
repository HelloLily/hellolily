# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..models import LilyUser, UserInfo

INCOMPLETE = 0
COMPLETED = 1


def set_completed_email_account_status(apps, schema_editor):
    LilyUser = apps.get_model('users', 'LilyUser')
    UserInfo = apps.get_model('users', 'UserInfo')
    EmailAccount = apps.get_model('email', 'EmailAccount')

    users = LilyUser.objects.all()

    for user in users:
        has_accounts = EmailAccount.objects.filter(owner=user).exists()

        if not has_accounts:
            status = INCOMPLETE
        else:
            status = COMPLETED

        user.info = UserInfo.objects.create(email_account_status=status)
        user.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20170206_1231'),
    ]

    operations = [
        migrations.RunPython(set_completed_email_account_status, do_nothing)
    ]
