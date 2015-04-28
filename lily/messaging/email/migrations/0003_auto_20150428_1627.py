# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0002_emailmessage_is_removed'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailoutboxmessage',
            name='original_attachment_ids',
            field=models.CommaSeparatedIntegerField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailoutboxmessage',
            name='template_attachment_ids',
            field=models.CommaSeparatedIntegerField(default=b'', max_length=255),
            preserve_default=True,
        ),
    ]
