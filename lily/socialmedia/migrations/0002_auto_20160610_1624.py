# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmedia',
            name='name',
            field=models.CharField(max_length=30, choices=[(b'facebook', 'Facebook'), (b'twitter', 'Twitter'), (b'linkedin', 'LinkedIn'), (b'googleplus', 'Google+'), (b'qzone', 'Qzone'), (b'orkut', 'Orkut'), (b'other', 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='socialmedia',
            name='profile_url',
            field=models.URLField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='socialmedia',
            name='username',
            field=models.CharField(max_length=100, blank=True),
            preserve_default=True,
        ),
    ]
