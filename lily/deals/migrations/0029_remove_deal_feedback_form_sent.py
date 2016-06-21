# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0028_auto_20160610_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deal',
            name='feedback_form_sent',
        ),
    ]
