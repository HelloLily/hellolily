# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('historylistitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='utils.HistoryListItem')),
                ('sent_date', models.DateTimeField(null=True, db_index=True)),
                ('is_seen', models.BooleanField(default=False, db_index=True)),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
            bases=('utils.historylistitem',),
        ),
        migrations.CreateModel(
            name='MessagesAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='deleted', editable=False, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('account_type', models.CharField(max_length=255)),
                ('shared_with', models.SmallIntegerField(default=0, choices=[(0, "Don't share"), (1, 'Everybody'), (2, 'Specific users')])),
                ('owner', models.ForeignKey(related_name='messages_accounts_owned', verbose_name='owner', to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_messaging.messagesaccount_set', editable=False, to='contenttypes.ContentType', null=True)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
                ('user_group', models.ManyToManyField(related_name='messages_accounts_shared', verbose_name='shared with', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'messaging account',
                'verbose_name_plural': 'messaging accounts',
            },
            bases=(models.Model,),
        ),
    ]
