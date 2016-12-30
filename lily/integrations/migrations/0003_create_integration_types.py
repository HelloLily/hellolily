# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

integration_types = [
    {
        'name': 'PandaDoc',
        'auth_url': 'https://app.pandadoc.com/oauth2/authorize?',
        'token_url': 'https://api.pandadoc.com/oauth2/access_token',
        'scope': 'read+write'
    },
    {
        'name': 'Moneybird',
        'auth_url': 'https://moneybird.com/oauth/authorize?',
        'token_url': 'https://moneybird.com/oauth/token',
        'scope': 'estimates+settings',
    },
]


def create_integration_types(apps, schema_editor):
    IntegrationType = apps.get_model('integrations', 'IntegrationType')

    for integration_type in integration_types:
        IntegrationType.objects.create(
            name=integration_type.get('name'),
            auth_url=integration_type.get('auth_url'),
            token_url=integration_type.get('token_url'),
            scope=integration_type.get('scope')
        )


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0002_integrationtype'),
    ]

    operations = [
        migrations.RunPython(create_integration_types, do_nothing),
    ]
