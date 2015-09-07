# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0005_auto_20150709_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='card_sent',
            field=models.BooleanField(default=False, choices=[(False, 'Writing it now'), (True, 'Done')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deal',
            name='twitter_checked',
            field=models.BooleanField(default=False, choices=[(False, 'Nearly'), (True, 'Done')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='is_checked',
            field=models.BooleanField(default=False, verbose_name='quote checked', choices=[(False, 'Almost'), (True, 'Done')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='quote_id',
            field=models.CharField(max_length=255, verbose_name='freedom quote id', blank=True),
            preserve_default=True,
        ),
    ]
