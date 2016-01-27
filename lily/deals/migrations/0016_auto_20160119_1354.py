# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0015_auto_20151223_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='card_sent',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='feedback_form_sent',
            field=models.BooleanField(default=False, verbose_name='feedback form sent'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='is_checked',
            field=models.BooleanField(default=False, verbose_name='quote checked'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='new_business',
            field=models.BooleanField(default=False, verbose_name='business'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='twitter_checked',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
