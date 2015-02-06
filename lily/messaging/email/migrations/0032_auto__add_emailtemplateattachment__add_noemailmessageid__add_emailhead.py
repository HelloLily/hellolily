# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailTemplateAttachment'
        db.create_table(u'email_emailtemplateattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['email.EmailTemplate'])),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('email', ['EmailTemplateAttachment'])

        # Adding model 'NoEmailMessageId'
        db.create_table(u'email_noemailmessageid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='no_messages', to=orm['email.EmailAccount'])),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('email', ['NoEmailMessageId'])

        # Adding model 'EmailHeader'
        db.create_table(u'email_emailheader', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='headers', to=orm['email.EmailMessage'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('email', ['EmailHeader'])

        # Adding model 'EmailAttachment'
        db.create_table(u'email_emailattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inline', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['email.EmailMessage'])),
        ))
        db.send_create_signal('email', ['EmailAttachment'])

        # Adding model 'EmailLabel'
        db.create_table(u'email_emaillabel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', to=orm['email.EmailAccount'])),
            ('label_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('unread', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('email', ['EmailLabel'])

        # Adding model 'GmailCredentialsModel'
        db.create_table(u'email_gmailcredentialsmodel', (
            ('id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['email.EmailAccount'], primary_key=True)),
            ('credentials', self.gf('oauth2client.django_orm.CredentialsField')(null=True)),
        ))
        db.send_create_signal('email', ['GmailCredentialsModel'])

        # Adding model 'EmailDraft'
        db.create_table(u'email_emaildraft', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('send_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='drafts', to=orm['email.EmailAccount'])),
            ('send_to_normal', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('send_to_cc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('send_to_bcc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('body_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('email', ['EmailDraft'])

        # Adding model 'EmailMessage'
        db.create_table(u'email_emailmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['email.EmailAccount'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_messages', to=orm['email.Recipient'])),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('thread_id', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('sent_date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('subject', self.gf('django.db.models.fields.TextField')(default='')),
            ('snippet', self.gf('django.db.models.fields.TextField')(default='')),
            ('has_attachment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('body_html', self.gf('django.db.models.fields.TextField')(default='')),
            ('body_text', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('email', ['EmailMessage'])

        # Adding M2M table for field labels on 'EmailMessage'
        m2m_table_name = db.shorten_name(u'email_emailmessage_labels')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailmessage', models.ForeignKey(orm['email.emailmessage'], null=False)),
            ('emaillabel', models.ForeignKey(orm['email.emaillabel'], null=False))
        ))
        db.create_unique(m2m_table_name, ['emailmessage_id', 'emaillabel_id'])

        # Adding M2M table for field received_by on 'EmailMessage'
        m2m_table_name = db.shorten_name(u'email_emailmessage_received_by')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailmessage', models.ForeignKey(orm['email.emailmessage'], null=False)),
            ('recipient', models.ForeignKey(orm['email.recipient'], null=False))
        ))
        db.create_unique(m2m_table_name, ['emailmessage_id', 'recipient_id'])

        # Adding M2M table for field received_by_cc on 'EmailMessage'
        m2m_table_name = db.shorten_name(u'email_emailmessage_received_by_cc')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailmessage', models.ForeignKey(orm['email.emailmessage'], null=False)),
            ('recipient', models.ForeignKey(orm['email.recipient'], null=False))
        ))
        db.create_unique(m2m_table_name, ['emailmessage_id', 'recipient_id'])

        # Adding unique constraint on 'EmailMessage', fields ['account', 'message_id']
        db.create_unique(u'email_emailmessage', ['account_id', 'message_id'])

        # Adding model 'EmailOutboxMessage'
        db.create_table(u'email_emailoutboxmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('send_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outbox_messages', to=orm['email.EmailAccount'])),
            ('to', self.gf('django.db.models.fields.TextField')()),
            ('cc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('bcc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('headers', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mapped_attachments', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('email', ['EmailOutboxMessage'])

        # Adding model 'EmailTemplate'
        db.create_table(u'email_emailtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('body_html', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('email', ['EmailTemplate'])

        # Adding model 'EmailOutboxAttachment'
        db.create_table(u'email_emailoutboxattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('inline', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email_outbox_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['email.EmailOutboxMessage'])),
        ))
        db.send_create_signal('email', ['EmailOutboxAttachment'])

        # Adding model 'EmailAccount'
        db.create_table(u'email_emailaccount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('from_name', self.gf('django.db.models.fields.CharField')(default='', max_length=254)),
            ('label', self.gf('django.db.models.fields.CharField')(default='', max_length=254)),
            ('is_authorized', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('history_id', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('temp_history_id', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='email_accounts_owned', to=orm['users.LilyUser'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('email', ['EmailAccount'])

        # Adding M2M table for field shared_with_users on 'EmailAccount'
        m2m_table_name = db.shorten_name(u'email_emailaccount_shared_with_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailaccount', models.ForeignKey(orm['email.emailaccount'], null=False)),
            ('lilyuser', models.ForeignKey(orm[u'users.lilyuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['emailaccount_id', 'lilyuser_id'])

        # Adding model 'DefaultEmailTemplate'
        db.create_table(u'email_defaultemailtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_templates', to=orm['users.LilyUser'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_templates', to=orm['email.EmailTemplate'])),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_templates', to=orm['email.EmailAccount'])),
        ))
        db.send_create_signal('email', ['DefaultEmailTemplate'])

        # Adding unique constraint on 'DefaultEmailTemplate', fields ['user', 'account']
        db.create_unique(u'email_defaultemailtemplate', ['user_id', 'account_id'])

        # Adding model 'Recipient'
        db.create_table(u'email_recipient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('email_address', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, db_index=True)),
        ))
        db.send_create_signal('email', ['Recipient'])

        # Adding unique constraint on 'Recipient', fields ['name', 'email_address']
        db.create_unique(u'email_recipient', ['name', 'email_address'])


    def backwards(self, orm):
        # Removing unique constraint on 'Recipient', fields ['name', 'email_address']
        db.delete_unique(u'email_recipient', ['name', 'email_address'])

        # Removing unique constraint on 'DefaultEmailTemplate', fields ['user', 'account']
        db.delete_unique(u'email_defaultemailtemplate', ['user_id', 'account_id'])

        # Removing unique constraint on 'EmailMessage', fields ['account', 'message_id']
        db.delete_unique(u'email_emailmessage', ['account_id', 'message_id'])

        # Deleting model 'EmailTemplateAttachment'
        db.delete_table(u'email_emailtemplateattachment')

        # Deleting model 'NoEmailMessageId'
        db.delete_table(u'email_noemailmessageid')

        # Deleting model 'EmailHeader'
        db.delete_table(u'email_emailheader')

        # Deleting model 'EmailAttachment'
        db.delete_table(u'email_emailattachment')

        # Deleting model 'EmailLabel'
        db.delete_table(u'email_emaillabel')

        # Deleting model 'GmailCredentialsModel'
        db.delete_table(u'email_gmailcredentialsmodel')

        # Deleting model 'EmailDraft'
        db.delete_table(u'email_emaildraft')

        # Deleting model 'EmailMessage'
        db.delete_table(u'email_emailmessage')

        # Removing M2M table for field labels on 'EmailMessage'
        db.delete_table(db.shorten_name(u'email_emailmessage_labels'))

        # Removing M2M table for field received_by on 'EmailMessage'
        db.delete_table(db.shorten_name(u'email_emailmessage_received_by'))

        # Removing M2M table for field received_by_cc on 'EmailMessage'
        db.delete_table(db.shorten_name(u'email_emailmessage_received_by_cc'))

        # Deleting model 'EmailOutboxMessage'
        db.delete_table(u'email_emailoutboxmessage')

        # Deleting model 'EmailTemplate'
        db.delete_table(u'email_emailtemplate')

        # Deleting model 'EmailOutboxAttachment'
        db.delete_table(u'email_emailoutboxattachment')

        # Deleting model 'EmailAccount'
        db.delete_table(u'email_emailaccount')

        # Removing M2M table for field shared_with_users on 'EmailAccount'
        db.delete_table(db.shorten_name(u'email_emailaccount_shared_with_users'))

        # Deleting model 'DefaultEmailTemplate'
        db.delete_table(u'email_defaultemailtemplate')

        # Deleting model 'Recipient'
        db.delete_table(u'email_recipient')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'email.defaultemailtemplate': {
            'Meta': {'unique_together': "(('user', 'account'),)", 'object_name': 'DefaultEmailTemplate'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_templates'", 'to': "orm['email.EmailAccount']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_templates'", 'to': "orm['email.EmailTemplate']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_templates'", 'to': u"orm['users.LilyUser']"})
        },
        'email.emailaccount': {
            'Meta': {'object_name': 'EmailAccount'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'from_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '254'}),
            'history_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_authorized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '254'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_accounts_owned'", 'to': u"orm['users.LilyUser']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shared_with_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'shared_email_accounts'", 'blank': 'True', 'to': u"orm['users.LilyUser']"}),
            'temp_history_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emailattachment': {
            'Meta': {'object_name': 'EmailAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['email.EmailMessage']"}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'email.emaildraft': {
            'Meta': {'object_name': 'EmailDraft'},
            'body_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'send_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'drafts'", 'to': "orm['email.EmailAccount']"}),
            'send_to_bcc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'send_to_cc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'send_to_normal': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'email.emailheader': {
            'Meta': {'object_name': 'EmailHeader'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'headers'", 'to': "orm['email.EmailMessage']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'email.emaillabel': {
            'Meta': {'object_name': 'EmailLabel'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['email.EmailAccount']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'label_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'unread': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'email.emailmessage': {
            'Meta': {'ordering': "['-sent_date']", 'unique_together': "(('account', 'message_id'),)", 'object_name': 'EmailMessage'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['email.EmailAccount']"}),
            'body_html': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'body_text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'has_attachment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'messages'", 'symmetrical': 'False', 'to': "orm['email.EmailLabel']"}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'received_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'received_messages'", 'symmetrical': 'False', 'to': "orm['email.Recipient']"}),
            'received_by_cc': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'received_messages_as_cc'", 'symmetrical': 'False', 'to': "orm['email.Recipient']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': "orm['email.Recipient']"}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'snippet': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'subject': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'thread_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'email.emailoutboxattachment': {
            'Meta': {'object_name': 'EmailOutboxAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email_outbox_message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['email.EmailOutboxMessage']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emailoutboxmessage': {
            'Meta': {'object_name': 'EmailOutboxMessage'},
            'bcc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'headers': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mapped_attachments': ('django.db.models.fields.IntegerField', [], {}),
            'send_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outbox_messages'", 'to': "orm['email.EmailAccount']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'to': ('django.db.models.fields.TextField', [], {})
        },
        'email.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'default_for': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['email.EmailAccount']", 'through': "orm['email.DefaultEmailTemplate']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emailtemplateattachment': {
            'Meta': {'object_name': 'EmailTemplateAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['email.EmailTemplate']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.gmailcredentialsmodel': {
            'Meta': {'object_name': 'GmailCredentialsModel'},
            'credentials': ('oauth2client.django_orm.CredentialsField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email.EmailAccount']", 'primary_key': 'True'})
        },
        'email.noemailmessageid': {
            'Meta': {'object_name': 'NoEmailMessageId'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'no_messages'", 'to': "orm['email.EmailAccount']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'email.recipient': {
            'Meta': {'unique_together': "(('name', 'email_address'),)", 'object_name': 'Recipient'},
            'email_address': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        },
        u'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'users.lilyuser': {
            'Meta': {'ordering': "['first_name', 'last_name']", 'object_name': 'LilyUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '3'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Europe/Amsterdam'"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        }
    }

    complete_apps = ['email']