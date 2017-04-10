# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0026_remove_emailaccount_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharedemailconfig',
            name='privacy',
            field=models.IntegerField(default=0, choices=[(0, 'Mailbox'), (1, 'Email'), (2, 'Metadata'), (3, 'Nothing')]),
        ),
    ]
