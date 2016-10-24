# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.messaging.email.models.models
import oauth2client.contrib.django_orm
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultEmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'default e-mail template',
                'verbose_name_plural': 'default e-mail templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='deleted', editable=False, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('email_address', models.EmailField(max_length=254)),
                ('from_name', models.CharField(default=b'', max_length=254)),
                ('label', models.CharField(default=b'', max_length=254)),
                ('is_authorized', models.BooleanField(default=False)),
                ('history_id', models.BigIntegerField(null=True)),
                ('temp_history_id', models.BigIntegerField(null=True)),
                ('public', models.BooleanField(default=False, help_text='Make the email account accessible for the whole company.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inline', models.BooleanField(default=False)),
                ('attachment', models.FileField(max_length=255, upload_to=lily.messaging.email.models.models.get_attachment_upload_path)),
                ('size', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailDraft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('send_to_normal', models.TextField(null=True, verbose_name='to', blank=True)),
                ('send_to_cc', models.TextField(null=True, verbose_name='cc', blank=True)),
                ('send_to_bcc', models.TextField(null=True, verbose_name='bcc', blank=True)),
                ('subject', models.CharField(max_length=255, null=True, verbose_name='subject', blank=True)),
                ('body_html', models.TextField(null=True, verbose_name='html body', blank=True)),
            ],
            options={
                'verbose_name': 'e-mail draft',
                'verbose_name_plural': 'e-mail drafts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label_type', models.IntegerField(default=0, choices=[(0, 'System'), (1, 'User')])),
                ('label_id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('unread', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_id', models.CharField(max_length=50, db_index=True)),
                ('thread_id', models.CharField(max_length=50, db_index=True)),
                ('sent_date', models.DateTimeField(db_index=True)),
                ('read', models.BooleanField(default=False, db_index=True)),
                ('subject', models.TextField(default=b'')),
                ('snippet', models.TextField(default=b'')),
                ('has_attachment', models.BooleanField(default=False)),
                ('body_html', models.TextField(default=b'')),
                ('body_text', models.TextField(default=b'')),
            ],
            options={
                'ordering': ['-sent_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailOutboxAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inline', models.BooleanField(default=False)),
                ('attachment', models.FileField(max_length=255, upload_to=lily.messaging.email.models.models.get_outbox_attachment_upload_path)),
                ('size', models.PositiveIntegerField(default=0)),
                ('content_type', models.CharField(max_length=255, verbose_name='content type')),
            ],
            options={
                'verbose_name': 'e-mail outbox attachment',
                'verbose_name_plural': 'e-mail outbox attachments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailOutboxMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255, null=True, verbose_name='subject', blank=True)),
                ('to', models.TextField(verbose_name='to')),
                ('cc', models.TextField(null=True, verbose_name='cc', blank=True)),
                ('bcc', models.TextField(null=True, verbose_name='bcc', blank=True)),
                ('body', models.TextField(null=True, verbose_name='html body', blank=True)),
                ('headers', models.TextField(null=True, verbose_name='email headers', blank=True)),
                ('mapped_attachments', models.IntegerField(verbose_name='number of mapped attachments')),
            ],
            options={
                'verbose_name': 'e-mail outbox message',
                'verbose_name_plural': 'e-mail outbox messages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='template name')),
                ('subject', models.CharField(max_length=255, verbose_name='message subject', blank=True)),
                ('body_html', models.TextField(verbose_name='html part', blank=True)),
            ],
            options={
                'verbose_name': 'e-mail template',
                'verbose_name_plural': 'e-mail templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailTemplateAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(upload_to=lily.messaging.email.models.models.get_template_attachment_upload_path, max_length=255, verbose_name='template attachment')),
                ('size', models.PositiveIntegerField(default=0)),
                ('content_type', models.CharField(max_length=255, verbose_name='content type')),
                ('template', models.ForeignKey(related_name='attachments', verbose_name='', to='email.EmailTemplate')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'e-mail template attachment',
                'verbose_name_plural': 'e-mail template attachments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GmailCredentialsModel',
            fields=[
                ('id', models.ForeignKey(primary_key=True, serialize=False, to='email.EmailAccount')),
                ('credentials', oauth2client.contrib.django_orm.CredentialsField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NoEmailMessageId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_id', models.CharField(max_length=50, db_index=True)),
                ('account', models.ForeignKey(related_name='no_messages', to='email.EmailAccount')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1000, null=True)),
                ('email_address', models.CharField(max_length=1000, null=True, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='recipient',
            unique_together=set([('name', 'email_address')]),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='default_for',
            field=models.ManyToManyField(to='email.EmailAccount', through='email.DefaultEmailTemplate'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailoutboxmessage',
            name='send_from',
            field=models.ForeignKey(related_name='outbox_messages', verbose_name='from', to='email.EmailAccount'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailoutboxmessage',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailoutboxattachment',
            name='email_outbox_message',
            field=models.ForeignKey(related_name='attachments', to='email.EmailOutboxMessage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailoutboxattachment',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailmessage',
            name='account',
            field=models.ForeignKey(related_name='messages', to='email.EmailAccount'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailmessage',
            name='labels',
            field=models.ManyToManyField(related_name='messages', to='email.EmailLabel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailmessage',
            name='received_by',
            field=models.ManyToManyField(related_name='received_messages', to='email.Recipient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailmessage',
            name='received_by_cc',
            field=models.ManyToManyField(related_name='received_messages_as_cc', to='email.Recipient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailmessage',
            name='sender',
            field=models.ForeignKey(related_name='sent_messages', to='email.Recipient'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='emailmessage',
            unique_together=set([('account', 'message_id')]),
        ),
        migrations.AddField(
            model_name='emaillabel',
            name='account',
            field=models.ForeignKey(related_name='labels', to='email.EmailAccount'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='emaillabel',
            unique_together=set([('account', 'label_id')]),
        ),
        migrations.AddField(
            model_name='emailheader',
            name='message',
            field=models.ForeignKey(related_name='headers', to='email.EmailMessage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emaildraft',
            name='send_from',
            field=models.ForeignKey(related_name='drafts', verbose_name='From', to='email.EmailAccount'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailattachment',
            name='message',
            field=models.ForeignKey(related_name='attachments', to='email.EmailMessage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailaccount',
            name='owner',
            field=models.ForeignKey(related_name='email_accounts_owned', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailaccount',
            name='shared_with_users',
            field=models.ManyToManyField(help_text='Select the users wich to share the account with.', related_name='shared_email_accounts', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailaccount',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultemailtemplate',
            name='account',
            field=models.ForeignKey(related_name='default_templates', to='email.EmailAccount'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultemailtemplate',
            name='template',
            field=models.ForeignKey(related_name='default_templates', to='email.EmailTemplate'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultemailtemplate',
            name='user',
            field=models.ForeignKey(related_name='default_templates', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='defaultemailtemplate',
            unique_together=set([('user', 'account')]),
        ),
    ]
