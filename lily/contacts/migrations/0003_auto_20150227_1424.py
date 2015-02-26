# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_auto_20150218_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='import_id',
            field=models.CharField(default=b'', max_length=100, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='first_name',
            field=models.CharField(default=b'', max_length=255, verbose_name='first name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='last_name',
            field=models.CharField(default=b'', max_length=255, verbose_name='last name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='preposition',
            field=models.CharField(default=b'', max_length=100, verbose_name='preposition', blank=True),
            preserve_default=True,
        ),
    ]
