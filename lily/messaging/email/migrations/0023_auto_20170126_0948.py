# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0022_auto_20170117_0849'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emaildraft',
            name='send_from',
        ),
        migrations.DeleteModel(
            name='EmailDraft',
        ),
    ]
