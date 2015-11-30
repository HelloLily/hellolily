# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        ('deals', '0009_auto_20151012_1730'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealNextStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('date_increment', models.IntegerField(default=0)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='deal',
            name='expected_closing_date',
        ),
        migrations.AddField(
            model_name='deal',
            name='next_step',
            field=models.ForeignKey(related_name='deals', verbose_name='next step', to='deals.DealNextStep', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deal',
            name='next_step_date',
            field=models.DateField(null=True, verbose_name='next step date', blank=True),
            preserve_default=True,
        ),
    ]
