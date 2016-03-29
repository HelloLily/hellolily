# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_lilyuser_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lilygroup',
            name='name',
            field=models.CharField(max_length=80, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='lilygroup',
            unique_together=set([('tenant', 'name')]),
        ),
    ]
