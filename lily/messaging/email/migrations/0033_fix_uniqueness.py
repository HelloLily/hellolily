# -*- coding: utf-8 -*-
from django.db.models import Min, Count
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        master_pks = orm.EmailLabel.objects.values('account_id', 'label_id'
            ).annotate(Min('pk'), count=Count('pk')
            ).filter(count__gt=1
            ).values_list('pk__min', flat=True)

        masters = orm.EmailLabel.objects.in_bulk( list(master_pks) )

        for master in masters.values():
            orm.EmailLabel.objects.filter(account_id=master.account_id, label_id=master.label_id
                ).exclude(pk=master.pk).delete()

    def backwards(self, orm):
        "Write your backwards methods here."



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
            'Meta': {'unique_together': "(('account', 'label_id'),)", 'object_name': 'EmailLabel'},
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
    symmetrical = True
