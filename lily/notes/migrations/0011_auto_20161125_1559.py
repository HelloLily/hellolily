# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0010_remove_polymorphic_cleanup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Note'), (1, 'Call'), (2, 'Meetup')]),
        ),
    ]
