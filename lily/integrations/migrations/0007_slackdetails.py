# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0006_slack_integrationtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlackDetails',
            fields=[
                ('integrationdetails_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='integrations.IntegrationDetails')),
                ('team_id', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('integrations.integrationdetails',),
        ),
    ]
