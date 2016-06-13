# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0004_auto_20160408_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='note',
            name='content',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='note',
            name='type',
            field=models.SmallIntegerField(default=0, max_length=2, choices=[(0, 'Note'), (1, 'Call'), (2, 'Meetup')]),
            preserve_default=True,
        ),
    ]
