# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0004_emailmessage_draft_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailattachment',
            name='cid',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
