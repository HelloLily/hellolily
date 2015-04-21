# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0002_auto_20150414_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='type',
            field=models.CharField(default=b'work', max_length=15, verbose_name='type', choices=[(b'work', 'Work'), (b'mobile', 'Mobile'), (b'home', 'Home'), (b'fax', 'Fax'), (b'other', 'Other')]),
            preserve_default=True,
        ),
    ]
