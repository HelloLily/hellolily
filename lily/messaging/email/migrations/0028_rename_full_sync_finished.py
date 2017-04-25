# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from ..models.models import EmailAccount


def toggle_sync_status(apps, schema_editor):
    EmailAccount = apps.get_model('email', 'EmailAccount')

    email_accounts = EmailAccount.objects.all()

    for email_account in email_accounts:
        email_account.is_syncing = not email_account.is_syncing
        email_account.save()


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0027_sharedemailconfig_privacy'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailaccount',
            old_name='full_sync_finished',
            new_name='is_syncing',
        ),
        migrations.RunPython(toggle_sync_status, toggle_sync_status)
    ]
