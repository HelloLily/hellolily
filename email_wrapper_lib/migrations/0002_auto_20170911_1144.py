# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_wrapper_lib', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emaildraftattachment',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='emaildraftattachment',
            name='size',
        ),
        migrations.AlterField(
            model_name='emaildraft',
            name='body_html',
            field=models.TextField(default=b'', verbose_name='Body html', blank=True),
        ),
        migrations.AlterField(
            model_name='emaildraft',
            name='body_text',
            field=models.TextField(default=b'', verbose_name='Body text', blank=True),
        ),
        migrations.AlterField(
            model_name='emaildraft',
            name='subject',
            field=models.CharField(default=b'', max_length=255, verbose_name='Subject', blank=True),
        ),
    ]
