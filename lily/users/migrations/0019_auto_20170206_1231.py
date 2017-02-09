# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20161207_1319'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_account_status', models.IntegerField(default=0, choices=[(0, 'Incomplete'), (1, 'Complete'), (2, 'Skipped')])),
            ],
        ),
        migrations.AddField(
            model_name='lilyuser',
            name='info',
            field=models.ForeignKey(blank=True, to='users.UserInfo', null=True),
        ),
    ]
