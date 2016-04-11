# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_lilyuser_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lilyuser',
            name='picture',
            field=models.ImageField(upload_to=lily.users.models.get_lilyuser_picture_upload_path, verbose_name='picture', blank=True),
            preserve_default=True,
        ),
    ]
