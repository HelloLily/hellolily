# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0008_templatevariable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatevariable',
            name='is_public',
            field=models.BooleanField(default=False, help_text=b'A public template variable is available to everyone in your organisation', choices=[(False, 'No'), (True, 'Yes')]),
            preserve_default=True,
        ),
    ]
