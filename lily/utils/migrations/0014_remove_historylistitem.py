# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0013_auto_20160603_1535'),
        ('notes', '0010_remove_polymorphic_cleanup')
    ]

    operations = [
        migrations.RemoveField(
            model_name='historylistitem',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='historylistitem',
            name='tenant',
        ),
        migrations.DeleteModel(
            name='HistoryListItem',
        ),
    ]
