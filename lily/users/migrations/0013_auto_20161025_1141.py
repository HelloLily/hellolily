# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import lily.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20161003_1426'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='lilyuser',
            managers=[
                ('objects', lily.users.models.LilyUserManager()),
            ],
        ),
        # Change the help_text.
        migrations.AlterField(
            model_name='lilyuser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        # Make nullable.
        migrations.AlterField(
            model_name='lilyuser',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
    ]
