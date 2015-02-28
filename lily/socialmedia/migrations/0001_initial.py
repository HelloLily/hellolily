# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='name', choices=[(b'facebook', 'Facebook'), (b'twitter', 'Twitter'), (b'linkedin', 'LinkedIn'), (b'googleplus', 'Google+'), (b'qzone', 'Qzone'), (b'orkut', 'Orkut'), (b'other', 'Other')])),
                ('other_name', models.CharField(max_length=30, null=True, blank=True)),
                ('username', models.CharField(max_length=100, verbose_name='username', blank=True)),
                ('profile_url', models.URLField(max_length=255, null=True, verbose_name='profile link', blank=True)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'social media',
                'verbose_name_plural': 'social media',
            },
            bases=(models.Model,),
        ),
    ]
