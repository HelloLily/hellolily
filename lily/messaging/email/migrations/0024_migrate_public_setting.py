# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..models.models import EmailAccount

PUBLIC = 0


def migrate_public_setting(apps, schema_editor):
    EmailAccount = apps.get_model('email', 'EmailAccount')

    email_accounts = EmailAccount.objects.all()

    for email_account in email_accounts:
        if email_account.public:
            email_account.privacy = PUBLIC
            email_account.save()

def migrate_public_setting_backwards(apps, schema_editor):
    EmailAccount = apps.get_model('email', 'EmailAccount')

    email_accounts = EmailAccount.objects.all()

    for email_account in email_accounts:
        if email_account.privacy == PUBLIC:
            email_account.public = True
            email_account.save()


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0023_emailaccount_privacy'),
    ]

    operations = [
        migrations.RunPython(migrate_public_setting, migrate_public_setting_backwards)
    ]
