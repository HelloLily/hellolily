# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0004_auto_20150527_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='feedback_form_sent',
            field=models.BooleanField(default=False, verbose_name='feedback form sent', choices=[(False, 'Not yet'), (True, 'Done')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='new_business',
            field=models.BooleanField(default=False, verbose_name='business', choices=[(False, 'Existing'), (True, 'New')]),
            preserve_default=True,
        ),
    ]
