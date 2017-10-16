# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_integration_type(apps, schema_editor):
    IntegrationType = apps.get_model('integrations', 'IntegrationType')

    data = {
        'name': 'Slack',
        'auth_url': 'https://slack.com/oauth/authorize?',
        'token_url': 'https://slack.com/api/oauth.access',
        'scope': 'links:read links:write',
    }

    IntegrationType.objects.create(
        name=data.get('name'),
        auth_url=data.get('auth_url'),
        token_url=data.get('token_url'),
        scope=data.get('scope')
    )


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0005_create_documentevent'),
    ]

    operations = [
        migrations.RunPython(create_integration_type, do_nothing),
    ]
