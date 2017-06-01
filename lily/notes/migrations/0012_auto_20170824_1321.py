# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0011_auto_20161125_1559'),
        ('calls', '0006_auto_20171011_0935'),
    ]

    operations = [
        migrations.RenameField(
            model_name='note',
            old_name='content_type',
            new_name='gfk_content_type',
        ),
        migrations.RenameField(
            model_name='note',
            old_name='object_id',
            new_name='gfk_object_id',
        ),
    ]
