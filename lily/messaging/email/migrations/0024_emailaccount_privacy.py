# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0023_auto_20170126_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaccount',
            name='privacy',
            field=models.IntegerField(default=1, choices=[(0, 'Mailbox'), (1, 'Email'), (2, 'Metadata'), (3, 'Nothing')]),
            preserve_default=True,
        ),
    ]
