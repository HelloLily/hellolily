# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0004_tenant_currency'),
        ('users', '0022_auto_20170508_1525'),
        ('email_wrapper_lib', '0002_auto_20170911_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAccountConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_name', models.CharField(default=b'', max_length=254, verbose_name='From name')),
                ('label', models.CharField(default=b'', max_length=254, verbose_name='Inbox label')),
                ('privacy', models.PositiveSmallIntegerField(default=0, verbose_name='Privacy', choices=[(0, 'Complete message'), (1, 'Date and recipients'), (2, 'Not at all')])),
                ('shared_with_everyone', models.BooleanField(default=False, verbose_name='Shared with everyone')),
                ('email_account', models.ForeignKey(verbose_name='Email account', to='email_wrapper_lib.EmailAccount')),
                ('owners', models.ManyToManyField(related_name='imelo_owned_email_accounts', verbose_name='Owned email accounts', to=settings.AUTH_USER_MODEL)),
                ('shared_with_teams', models.ManyToManyField(related_name='imelo_shared_email_accounts', verbose_name='Shared with teams', to='users.Team')),
                ('shared_with_users', models.ManyToManyField(related_name='imelo_shared_email_accounts', verbose_name='Shared with users', to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
