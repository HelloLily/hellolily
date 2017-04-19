# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0018_auto_20170418_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='type',
            field=models.ForeignKey(related_name='cases', to='cases.CaseType'),
        ),
    ]
