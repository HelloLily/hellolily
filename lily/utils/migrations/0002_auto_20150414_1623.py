# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaddress',
            name='is_primary',
            field=models.BooleanField(default=False, verbose_name='primary e-mail', choices=[(False, 'Other'), (True, 'Primary')]),
            preserve_default=True,
        ),
    ]
