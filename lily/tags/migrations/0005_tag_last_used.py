# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0004_auto_20160610_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='last_used',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True),
            preserve_default=True,
        ),
    ]
