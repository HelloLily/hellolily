# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0002_auto_20160408_1519'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogentry',
            name='author',
        ),
        migrations.RemoveField(
            model_name='blogentry',
            name='reply_to',
        ),
        migrations.RemoveField(
            model_name='blogentry',
            name='tenant',
        ),
        migrations.DeleteModel(
            name='BlogEntry',
        ),
    ]
