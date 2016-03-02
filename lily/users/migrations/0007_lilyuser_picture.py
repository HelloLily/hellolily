# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20160321_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='lilyuser',
            name='picture',
            field=models.ImageField(upload_to=b'images/profile/user', verbose_name='picture', blank=True),
            preserve_default=True,
        ),
    ]
