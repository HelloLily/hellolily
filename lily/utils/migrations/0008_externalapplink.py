# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0002_tenant_name'),
        ('utils', '0007_auto_20160314_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalAppLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
