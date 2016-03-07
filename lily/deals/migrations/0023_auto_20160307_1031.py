# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        ('deals', '0022_auto_20160222_1513'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealWhyLost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('position', models.IntegerField(default=9, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)])),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deal',
            name='why_lost',
            field=models.ForeignKey(related_name='deals', verbose_name='why lost', to='deals.DealWhyLost', null=True),
            preserve_default=True,
        ),
    ]
