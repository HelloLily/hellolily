# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0003_note_is_pinned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='note',
            name='deleted',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='note',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified'),
            preserve_default=True,
        ),
    ]
