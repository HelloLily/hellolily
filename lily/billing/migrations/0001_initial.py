# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('tier', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subscription_id', models.CharField(max_length=255, blank=True)),
                ('customer_id', models.CharField(max_length=255, blank=True)),
                ('plan', models.ForeignKey(blank=True, to='billing.Plan', null=True)),
                ('cancels_on', models.DateTimeField(null=True, blank=True)),
                ('trial_started', models.BooleanField(default=False)),
            ],
        ),
    ]
