# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_first_sync_finished(apps, schema_editor):
    EmailAccount = apps.get_model('email', 'EmailAccount')

    email_accounts = EmailAccount.objects.all()

    for email_account in email_accounts:
        email_account.update_modified = False
        email_account.first_sync_finished = True
        email_account.save()


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0015_emailaccount_first_sync_finished'),
    ]

    operations = [
        migrations.RunPython(set_first_sync_finished),
    ]
