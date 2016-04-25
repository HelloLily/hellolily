# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0002_tenant_name'),
        ('accounts', '0009_auto_20160411_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('position', models.IntegerField(default=0, max_length=2)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={'ordering': ['position'], 'verbose_name_plural': 'account statuses'},
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='account',
            old_name='status',
            new_name='status_old',
        ),
        migrations.AddField(
            model_name='account',
            name='status',
            # default=3 Corresponds with the new status Relation, which was the old default value 'inactive'.
            # This value is overwritten by the follow-up migration, but IntegerField expect a default value.
            field=models.IntegerField(verbose_name='status', default=3, max_length=1),
            preserve_default=True
        ),
    ]
