# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import email_wrapper_lib.models.models
import oauth2client.contrib.django_orm
import django.db.models.deletion
import email_wrapper_lib.models.mixins


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=255, verbose_name='Username')),
                ('user_id', models.CharField(unique=True, max_length=255, verbose_name='User id')),
                ('credentials', oauth2client.contrib.django_orm.CredentialsField(null=True)),
                ('status', models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='Status', choices=[(0, 'new'), (1, 'idle'), (2, 'syncing'), (3, 'error'), (4, 'resync')])),
                ('provider_id', models.PositiveSmallIntegerField(db_index=True, verbose_name='Provider id', choices=[(1, b'google'), (2, b'microsoft')])),
                ('subscription_id', models.CharField(max_length=255, null=True, verbose_name='Subscription id')),
                ('history_token', models.CharField(max_length=255, null=True, verbose_name='History token')),
                ('page_token', models.CharField(max_length=255, null=True, verbose_name='Page token')),
            ],
            bases=(email_wrapper_lib.models.mixins.SoftDeleteMixin, email_wrapper_lib.models.mixins.TimeStampMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EmailDraft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255)),
                ('body_text', models.TextField(default=b'', verbose_name='body text', blank=True)),
                ('body_html', models.TextField(default=b'', verbose_name='body html', blank=True)),
                ('account', models.ForeignKey(related_name='drafts', verbose_name='Account', to='email_wrapper_lib.EmailAccount')),
            ],
        ),
        migrations.CreateModel(
            name='EmailDraftAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inline', models.BooleanField(default=False, verbose_name='Inline')),
                ('file', models.FileField(upload_to=email_wrapper_lib.models.models.attachment_upload_path, max_length=255, verbose_name='File')),
                ('size', models.PositiveIntegerField(default=0, verbose_name='Size')),
                ('content_type', models.CharField(max_length=255, verbose_name='Content type')),
                ('draft', models.ForeignKey(related_name='attachments', to='email_wrapper_lib.EmailDraft')),
            ],
            options={
                'verbose_name': 'email outbox attachment',
                'verbose_name_plural': 'email outbox attachments',
            },
        ),
        migrations.CreateModel(
            name='EmailDraftToEmailRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient_type', models.PositiveSmallIntegerField(verbose_name='Recipient type', choices=[(0, 'To'), (1, 'CC'), (2, 'BCC')])),
                ('draft', models.ForeignKey(verbose_name='Draft', to='email_wrapper_lib.EmailDraft')),
            ],
        ),
        migrations.CreateModel(
            name='EmailFolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_id', models.CharField(max_length=255, null=True, verbose_name='Parent')),
                ('remote_id', models.CharField(max_length=255, verbose_name='Remote id')),
                ('remote_value', models.CharField(max_length=255, verbose_name='Remote value')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('folder_type', models.PositiveSmallIntegerField(verbose_name='Folder type', choices=[(0, 'System'), (1, 'User')])),
                ('unread_count', models.PositiveIntegerField(verbose_name='Unread count')),
                ('account', models.ForeignKey(related_name='folders', verbose_name='Account', to='email_wrapper_lib.EmailAccount')),
            ],
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('remote_id', models.CharField(max_length=255, verbose_name='Remote id')),
                ('thread_id', models.CharField(max_length=255, verbose_name='Thread id')),
                ('message_id', models.CharField(max_length=255, verbose_name='Message id')),
                ('snippet', models.CharField(max_length=255, verbose_name='Snippet')),
                ('subject', models.CharField(max_length=255, verbose_name='Subject')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('is_read', models.BooleanField(verbose_name='Is read')),
                ('is_starred', models.BooleanField(verbose_name='Is starred')),
                ('account', models.ForeignKey(related_name='messages', verbose_name='Account', to='email_wrapper_lib.EmailAccount')),
                ('folder', models.ManyToManyField(related_name='messages', verbose_name='Folder', to='email_wrapper_lib.EmailFolder')),
            ],
        ),
        migrations.CreateModel(
            name='EmailMessageToEmailRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient_type', models.PositiveSmallIntegerField(verbose_name='Recipient type', choices=[(0, 'To'), (1, 'CC'), (2, 'BCC'), (3, 'From'), (4, 'Sender'), (5, 'Reply to')])),
                ('message', models.ForeignKey(verbose_name='Message', to='email_wrapper_lib.EmailMessage')),
            ],
        ),
        migrations.CreateModel(
            name='EmailRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('email_address', models.EmailField(max_length=254, verbose_name='Email')),
                ('raw_value', models.CharField(unique=True, max_length=255, verbose_name='Raw value', db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='emailmessagetoemailrecipient',
            name='recipient',
            field=models.ForeignKey(verbose_name='Recipient', to='email_wrapper_lib.EmailRecipient'),
        ),
        migrations.AddField(
            model_name='emailmessage',
            name='recipients',
            field=models.ManyToManyField(related_name='messages', verbose_name='Recipients', through='email_wrapper_lib.EmailMessageToEmailRecipient', to='email_wrapper_lib.EmailRecipient'),
        ),
        migrations.AddField(
            model_name='emaildrafttoemailrecipient',
            name='recipient',
            field=models.ForeignKey(verbose_name='Recipient', to='email_wrapper_lib.EmailRecipient'),
        ),
        migrations.AddField(
            model_name='emaildraft',
            name='in_reply_to',
            field=models.ForeignKey(related_name='draft_replies', on_delete=django.db.models.deletion.SET_NULL, verbose_name='In reply to', to='email_wrapper_lib.EmailMessage', null=True),
        ),
        migrations.AddField(
            model_name='emaildraft',
            name='recipients',
            field=models.ManyToManyField(related_name='drafts', verbose_name='Recipients', through='email_wrapper_lib.EmailDraftToEmailRecipient', to='email_wrapper_lib.EmailRecipient'),
        ),
        migrations.AlterUniqueTogether(
            name='emailfolder',
            unique_together=set([('account', 'remote_id', 'remote_value')]),
        ),
    ]
