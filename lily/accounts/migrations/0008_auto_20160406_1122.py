# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160224_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='logo',
            field=models.ImageField(upload_to=lily.accounts.models.get_account_logo_upload_path, verbose_name='logo', blank=True),
            preserve_default=True,
        ),
    ]
