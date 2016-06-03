# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0012_generalize_address_cleanup'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailaddress',
            options={'verbose_name': 'email address', 'verbose_name_plural': 'email addresses'},
        ),
        migrations.AlterField(
            model_name='emailaddress',
            name='email_address',
            field=models.EmailField(max_length=255, verbose_name='email address'),
            preserve_default=True,
        ),
    ]
