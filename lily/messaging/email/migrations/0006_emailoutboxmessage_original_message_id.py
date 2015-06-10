# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0005_emailattachment_cid'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailoutboxmessage',
            name='original_message_id',
            field=models.CharField(db_index=True, max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
