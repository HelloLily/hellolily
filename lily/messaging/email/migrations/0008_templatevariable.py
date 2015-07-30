# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('email', '0007_auto_20150629_1456'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='variable name')),
                ('text', models.TextField(verbose_name='variable text')),
                ('is_public', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(related_name='template_variable', to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'e-mail template variable',
                'verbose_name_plural': 'e-mail template variables',
            },
            bases=(models.Model,),
        ),
    ]
