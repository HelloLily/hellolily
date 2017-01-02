# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20161125_1611'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lilyuser',
            unique_together=set([('tenant', 'internal_number')]),
        ),
    ]
