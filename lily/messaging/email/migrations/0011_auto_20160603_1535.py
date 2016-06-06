# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0010_auto_20160408_1519'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='defaultemailtemplate',
            options={'verbose_name': 'default email template', 'verbose_name_plural': 'default email templates'},
        ),
        migrations.AlterModelOptions(
            name='emaildraft',
            options={'verbose_name': 'email draft', 'verbose_name_plural': 'email drafts'},
        ),
        migrations.AlterModelOptions(
            name='emailoutboxattachment',
            options={'verbose_name': 'email outbox attachment', 'verbose_name_plural': 'email outbox attachments'},
        ),
        migrations.AlterModelOptions(
            name='emailoutboxmessage',
            options={'verbose_name': 'email outbox message', 'verbose_name_plural': 'email outbox messages'},
        ),
        migrations.AlterModelOptions(
            name='emailtemplate',
            options={'verbose_name': 'email template', 'verbose_name_plural': 'email templates'},
        ),
        migrations.AlterModelOptions(
            name='emailtemplateattachment',
            options={'verbose_name': 'email template attachment', 'verbose_name_plural': 'email template attachments'},
        ),
        migrations.AlterModelOptions(
            name='templatevariable',
            options={'verbose_name': 'email template variable', 'verbose_name_plural': 'email template variables'},
        ),
    ]
