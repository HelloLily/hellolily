# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'EmailTemplate.description'
        db.delete_column(u'email_emailtemplate', 'description')


    def backwards(self, orm):
        # Adding field 'EmailTemplate.description'
        db.add_column(u'email_emailtemplate', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


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
        'email.actionstep': {
            'Meta': {'object_name': 'ActionStep'},
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email.EmailMessage']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.defaultemailtemplate': {
            'Meta': {'unique_together': "(('user', 'account'),)", 'object_name': 'DefaultEmailTemplate'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_templates'", 'to': "orm['email.EmailAccount']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_templates'", 'to': "orm['email.EmailTemplate']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_templates'", 'to': u"orm['users.LilyUser']"})
        },
        'email.emailaccount': {
            'Meta': {'ordering': "['email']", 'object_name': 'EmailAccount', '_ormbases': [u'messaging.MessagesAccount']},
            'auth_ok': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'folders': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'from_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'last_sync_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            u'messagesaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['messaging.MessagesAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django_fields.fields.EncryptedCharField', [], {'max_length': '558', 'block_type': "'MODE_CBC'", 'cipher': "'AES'"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_accounts'", 'to': "orm['email.EmailProvider']"}),
            'username': ('django_fields.fields.EncryptedCharField', [], {'max_length': '558', 'block_type': "'MODE_CBC'", 'cipher': "'AES'"})
        },
        'email.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'email.emailaddressheader': {
            'Meta': {'object_name': 'EmailAddressHeader'},
            'email_address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email.EmailAddress']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email.EmailMessage']"}),
            'message_identifier': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_index': 'True'})
        },
        'email.emailattachment': {
            'Meta': {'object_name': 'EmailAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['email.EmailMessage']"}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'email.emaillabel': {
            'Meta': {'object_name': 'EmailLabel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['email.EmailMessage']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'email.emailmessage': {
            'Meta': {'unique_together': "(('uid', 'folder_name', 'account'),)", 'object_name': 'EmailMessage', '_ormbases': [u'messaging.Message'], 'index_together': "[['folder_name', 'account']]"},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['email.EmailAccount']"}),
            'body_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'flags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'folder_identifier': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['messaging.Message']", 'unique': 'True', 'primary_key': 'True'}),
            'sent_from_account': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'uid': ('django.db.models.fields.IntegerField', [], {})
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
        'email.emailprovider': {
            'Meta': {'object_name': 'EmailProvider'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imap_host': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'imap_port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'imap_ssl': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'smtp_host': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'smtp_port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'smtp_ssl': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'null': 'True', 'blank': 'True'})
        },
        'email.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'email.emailtemplateattachment': {
            'Meta': {'object_name': 'EmailTemplateAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['email.EmailTemplate']"})
        },
        u'messaging.message': {
            'Meta': {'object_name': 'Message', '_ormbases': ['utils.HistoryListItem']},
            u'historylistitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['utils.HistoryListItem']", 'unique': 'True', 'primary_key': 'True'}),
            'is_seen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'messaging.messagesaccount': {
            'Meta': {'object_name': 'MessagesAccount'},
            'account_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages_accounts_owned'", 'to': u"orm['users.LilyUser']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_messaging.messagesaccount_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'shared_with': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'user_group': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'messages_accounts_shared'", 'symmetrical': 'False', 'to': u"orm['users.LilyUser']"})
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
        },
        'utils.historylistitem': {
            'Meta': {'object_name': 'HistoryListItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_utils.historylistitem_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sort_by_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        }
    }

    complete_apps = ['email']