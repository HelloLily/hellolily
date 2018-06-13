# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0007_auto_20160411_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email_addresses',
            field=models.ManyToManyField(
                to='utils.EmailAddress',
                verbose_name='list of email addresses',
                blank=True
            ),
            preserve_default=True,
        ),
    ]
