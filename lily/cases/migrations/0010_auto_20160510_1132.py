# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0009_auto_20160414_1022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='casestatus',
            old_name='status',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='casetype',
            old_name='type',
            new_name='name',
        ),
    ]
