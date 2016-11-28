# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0020_truncate_noemailmessageid_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gmailcredentialsmodel',
            name='id',
            field=models.OneToOneField(primary_key=True, serialize=False, to='email.EmailAccount'),
        ),
    ]
