# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0003_auto_20150428_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='draft_id',
            field=models.CharField(default=b'', max_length=50, db_index=True),
            preserve_default=True,
        ),
    ]
