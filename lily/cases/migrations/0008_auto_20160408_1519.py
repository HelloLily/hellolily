# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0007_auto_20160127_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='deleted',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified'),
            preserve_default=True,
        ),
    ]
