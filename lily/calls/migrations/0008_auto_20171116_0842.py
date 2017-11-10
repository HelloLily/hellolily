# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0007_auto_20171019_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calltransfer',
            name='destination',
            field=models.ForeignKey(related_name='transfers_received', verbose_name='To', to='calls.CallParticipant', null=True),
        ),
    ]
