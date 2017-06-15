# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0017_auto_20161125_1601'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailaddress',
            options={'ordering': ['-status'], 'verbose_name': 'email address', 'verbose_name_plural': 'email addresses'},
        ),
    ]
