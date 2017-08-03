# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_tenant_currency'),
        ('email', '0030_truncate_noemailmessageid_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplateFolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='folder',
            field=models.ForeignKey(related_name='email_templates', blank=True, to='email.EmailTemplateFolder', null=True),
        ),
    ]
