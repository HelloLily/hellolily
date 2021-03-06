# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-08-22 13:03
from __future__ import unicode_literals

from django.db import migrations
import lily.utils.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0012_auto_20170824_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='created',
            field=lily.utils.models.fields.CreatedDateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='note',
            name='modified',
            field=lily.utils.models.fields.ModifiedDateTimeField(auto_now=True, verbose_name='modified'),
        ),
    ]
