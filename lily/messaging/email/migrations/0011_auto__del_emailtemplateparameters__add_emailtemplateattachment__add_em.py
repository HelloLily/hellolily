# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'EmailTemplateParameters'
        db.delete_table('email_emailtemplateparameters')

        # Adding model 'EmailTemplateAttachment'
        db.create_table('email_emailtemplateattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['email.EmailTemplate'])),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('email', ['EmailTemplateAttachment'])

        # Adding model 'EmailDraft'
        db.create_table('email_emaildraft', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('send_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='drafts', to=orm['email.EmailAccount'])),
            ('send_to_normal', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('send_to_cc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('send_to_bcc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('email', ['EmailDraft'])

        # Deleting field 'EmailTemplate.body'
        db.delete_column('email_emailtemplate', 'body')

        # Adding field 'EmailTemplate.created'
        db.add_column('email_emailtemplate', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True),
                      keep_default=False)

        # Adding field 'EmailTemplate.modified'
        db.add_column('email_emailtemplate', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True),
                      keep_default=False)

        # Adding field 'EmailTemplate.description'
        db.add_column('email_emailtemplate', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'EmailTemplate.subject'
        db.add_column('email_emailtemplate', 'subject',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'EmailTemplate.body_html'
        db.add_column('email_emailtemplate', 'body_html',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'EmailTemplate.body_text'
        db.add_column('email_emailtemplate', 'body_text',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Renaming field 'EmailProvider.send_use_tls'
        db.rename_column('email_emailprovider', 'send_use_tls', 'smtp_ssl')

        # Renaming field 'EmailProvider.retrieve_host'
        db.rename_column('email_emailprovider', 'retrieve_host', 'imap_host')

        # Renaming field 'EmailProvider.send_host'
        db.rename_column('email_emailprovider', 'send_host', 'smtp_host')

        # Renaming field 'EmailProvider.retrieve_port'
        db.rename_column('email_emailprovider', 'retrieve_port', 'imap_port')

        # Renaming field 'EmailProvider.send_port'
        db.rename_column('email_emailprovider', 'send_port', 'smtp_port')

        # # Adding field 'EmailProvider.imap_host'
        # db.add_column('email_emailprovider', 'imap_host',
        #               self.gf('django.db.models.fields.CharField')(default='smtp.example.com', max_length=32),
        #               keep_default=False)

        # # Adding field 'EmailProvider.imap_port'
        # db.add_column('email_emailprovider', 'imap_port',
        #               self.gf('django.db.models.fields.IntegerField')(default=443),
        #               keep_default=False)

        # Adding field 'EmailProvider.imap_ssl'
        db.add_column('email_emailprovider', 'imap_ssl',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # # Adding field 'EmailProvider.smtp_host'
        # db.add_column('email_emailprovider', 'smtp_host',
        #               self.gf('django.db.models.fields.CharField')(default='smtp.example.com', max_length=32),
        #               keep_default=False)

        # # Adding field 'EmailProvider.smtp_port'
        # db.add_column('email_emailprovider', 'smtp_port',
        #               self.gf('django.db.models.fields.IntegerField')(default=993),
        #               keep_default=False)

        # # Adding field 'EmailProvider.smtp_ssl'
        # db.add_column('email_emailprovider', 'smtp_ssl',
        #               self.gf('django.db.models.fields.BooleanField')(default=False),
        #               keep_default=False)


    def backwards(self, orm):
        # Adding model 'EmailTemplateParameters'
        db.create_table('email_emailtemplateparameters', (
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parameters', to=orm['email.EmailTemplate'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
        ))
        db.send_create_signal('email', ['EmailTemplateParameters'])

        # Deleting model 'EmailTemplateAttachment'
        db.delete_table('email_emailtemplateattachment')

        # Deleting model 'EmailDraft'
        db.delete_table('email_emaildraft')


        # User chose to not deal with backwards NULL issues for 'EmailTemplate.body'
        raise RuntimeError("Cannot reverse this migration. 'EmailTemplate.body' and its values cannot be restored.")
        # Deleting field 'EmailTemplate.created'
        db.delete_column('email_emailtemplate', 'created')

        # Deleting field 'EmailTemplate.modified'
        db.delete_column('email_emailtemplate', 'modified')

        # Deleting field 'EmailTemplate.description'
        db.delete_column('email_emailtemplate', 'description')

        # Deleting field 'EmailTemplate.subject'
        db.delete_column('email_emailtemplate', 'subject')

        # Deleting field 'EmailTemplate.body_html'
        db.delete_column('email_emailtemplate', 'body_html')

        # Deleting field 'EmailTemplate.body_text'
        db.delete_column('email_emailtemplate', 'body_text')

        # Adding field 'EmailProvider.send_use_tls'
        db.add_column('email_emailprovider', 'send_use_tls',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'EmailProvider.retrieve_host'
        raise RuntimeError("Cannot reverse this migration. 'EmailProvider.retrieve_host' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'EmailProvider.send_host'
        raise RuntimeError("Cannot reverse this migration. 'EmailProvider.send_host' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'EmailProvider.retrieve_port'
        raise RuntimeError("Cannot reverse this migration. 'EmailProvider.retrieve_port' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'EmailProvider.send_port'
        raise RuntimeError("Cannot reverse this migration. 'EmailProvider.send_port' and its values cannot be restored.")
        # Deleting field 'EmailProvider.imap_host'
        db.delete_column('email_emailprovider', 'imap_host')

        # Deleting field 'EmailProvider.imap_port'
        db.delete_column('email_emailprovider', 'imap_port')

        # Deleting field 'EmailProvider.imap_ssl'
        db.delete_column('email_emailprovider', 'imap_ssl')

        # Deleting field 'EmailProvider.smtp_host'
        db.delete_column('email_emailprovider', 'smtp_host')

        # Deleting field 'EmailProvider.smtp_port'
        db.delete_column('email_emailprovider', 'smtp_port')

        # Deleting field 'EmailProvider.smtp_ssl'
        db.delete_column('email_emailprovider', 'smtp_ssl')


    models = {
        'accounts.account': {
            'Meta': {'ordering': "['name']", 'object_name': 'Account'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'bankaccountnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'bic': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cocnumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'company_size': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'flatname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'legalentity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'taxnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contacts.contact': {
            'Meta': {'object_name': 'Contact'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'email.actionstep': {
            'Meta': {'object_name': 'ActionStep'},
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email.EmailMessage']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emailaccount': {
            'Meta': {'object_name': 'EmailAccount', '_ormbases': ['messaging.MessagesAccount']},
            'email': ('django_fields.fields.EncryptedEmailField', [], {'max_length': '549', 'cipher': "'AES'"}),
            'last_sync_date': ('django.db.models.fields.DateTimeField', [], {}),
            'messagesaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['messaging.MessagesAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django_fields.fields.EncryptedCharField', [], {'max_length': '549', 'cipher': "'AES'"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_accounts'", 'to': "orm['email.EmailProvider']"}),
            'username': ('django_fields.fields.EncryptedCharField', [], {'max_length': '549', 'cipher': "'AES'"})
        },
        'email.emailattachment': {
            'Meta': {'object_name': 'EmailAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['email.EmailMessage']"}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emaildraft': {
            'Meta': {'object_name': 'EmailDraft'},
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'send_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'drafts'", 'to': "orm['email.EmailAccount']"}),
            'send_to_bcc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'send_to_cc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'send_to_normal': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'email.emailheader': {
            'Meta': {'object_name': 'EmailHeader'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'headers'", 'to': "orm['email.EmailMessage']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'email.emaillabel': {
            'Meta': {'object_name': 'EmailLabel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['email.EmailMessage']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'email.emailmessage': {
            'Meta': {'unique_together': "(('uid', 'folder_name', 'account'),)", 'object_name': 'EmailMessage'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['messaging.MessagesAccount']"}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'flags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'folder_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_seen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_email.emailmessage_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'uid': ('django.db.models.fields.IntegerField', [], {})
        },
        'email.emailprovider': {
            'Meta': {'object_name': 'EmailProvider'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imap_host': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'imap_port': ('django.db.models.fields.IntegerField', [], {}),
            'imap_ssl': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'smtp_host': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'smtp_port': ('django.db.models.fields.IntegerField', [], {}),
            'smtp_ssl': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emailtemplateattachment': {
            'Meta': {'object_name': 'EmailTemplateAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['email.EmailTemplate']"})
        },
        'messaging.messagesaccount': {
            'Meta': {'object_name': 'MessagesAccount'},
            'account_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_messaging.messagesaccount_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'user_group': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'messages_accounts'", 'symmetrical': 'False', 'to': "orm['users.CustomUser']"})
        },
        'notes.note': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Note'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.CustomUser']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'tags.tag': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'object_id'),)", 'object_name': 'Tag'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'users.customuser': {
            'Meta': {'ordering': "['contact']", 'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': "orm['accounts.Account']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': "orm['contacts.Contact']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'utils.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'utils.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'utils.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
        },
        'utils.socialmedia': {
            'Meta': {'object_name': 'SocialMedia'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['email']
