# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='type',
            field=models.SmallIntegerField(default=0, max_length=2, verbose_name='type', choices=[(0, 'Note'), (1, 'Call'), (2, 'Meetup')]),
            preserve_default=True,
        ),
    ]
