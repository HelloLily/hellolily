# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='historylistitem_ptr',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.RemoveField(
            model_name='messagesaccount',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='messagesaccount',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='messagesaccount',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='messagesaccount',
            name='user_group',
        ),
        migrations.DeleteModel(
            name='MessagesAccount',
        ),
    ]
