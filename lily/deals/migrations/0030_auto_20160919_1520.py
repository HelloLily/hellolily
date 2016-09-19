# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0029_remove_deal_feedback_form_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='deleted',
            field=models.DateTimeField(verbose_name='deleted'),
            preserve_default=True,
        ),
    ]
