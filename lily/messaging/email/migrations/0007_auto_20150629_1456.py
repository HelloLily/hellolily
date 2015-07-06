# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('email', '0006_emailoutboxmessage_original_message_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedEmailConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('email_account', models.ForeignKey(to='email.EmailAccount')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sharedemailconfig',
            unique_together=set([('tenant', 'email_account', 'user')]),
        ),
    ]
