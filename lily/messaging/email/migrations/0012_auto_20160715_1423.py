# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0011_auto_20160603_1535'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='defaultemailtemplate',
            unique_together=set([('user', 'account', 'template')]),
        ),
    ]
