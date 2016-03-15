# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_lilyuser_primary_email_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='lilyuser',
            name='position',
            field=models.CharField(max_length=255, verbose_name='position', blank=True),
            preserve_default=True,
        ),
    ]
