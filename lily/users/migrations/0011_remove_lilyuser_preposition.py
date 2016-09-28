# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def merge_preposition(apps, schema_editor):
    LilyUser = apps.get_model('users', 'LilyUser')

    for user in LilyUser.objects.all():
        if user.preposition:
            user.last_name = ' '.join([user.preposition, user.last_name])
            user.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_teams'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lilyuser',
            name='first_name',
            field=models.CharField(max_length=255, verbose_name='first name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lilyuser',
            name='last_name',
            field=models.CharField(max_length=255, verbose_name='last name'),
            preserve_default=True,
        ),
        migrations.RunPython(merge_preposition, do_nothing),
        migrations.RemoveField(
            model_name='lilyuser',
            name='preposition',
        ),
    ]
