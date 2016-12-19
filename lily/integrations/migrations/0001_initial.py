# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import oauth2client.contrib.django_orm


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_tenant_currency'),
        ('contacts', '0012_remove_contact_preposition'),
        ('deals', '0032_deal_newly_assigned'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_id', models.CharField(max_length=255)),
                ('contact', models.ForeignKey(to='contacts.Contact')),
                ('deal', models.ForeignKey(to='deals.Deal')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntegrationDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(choices=[(0, 'PandaDoc'), (1, 'Slack')])),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntegrationCredentials',
            fields=[
                ('details', models.OneToOneField(primary_key=True, serialize=False, to='integrations.IntegrationDetails')),
                ('credentials', oauth2client.contrib.django_orm.CredentialsField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='integrationdetails',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='integrationdetails',
            unique_together=set([('tenant', 'type')]),
        ),
    ]
