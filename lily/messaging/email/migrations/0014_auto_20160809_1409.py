# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0013_fix_multple_default_templates'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='defaultemailtemplate',
            unique_together=set([('user', 'account')]),
        ),
    ]
