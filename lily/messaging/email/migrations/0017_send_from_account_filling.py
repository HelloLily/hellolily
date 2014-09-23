# -*- coding: utf-8 -*-
import email

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from django.conf import settings
from lily.utils.logutil import print_progress


class Migration(DataMigration):

    def forwards(self, orm):
        """
        Check for every EmailMessage if it was sent from related account.
        """
        if settings.SOUTH_VERBOSITY > 0:
            print 'DataMigration for setting the sent_from_account property of all EmailMessages '

        total_messages = orm.EmailMessage.objects.all().count()
        messages_ids = orm.EmailMessage.objects.all().values_list('id')
        i = 0
        for message_id in messages_ids:
            message = orm.EmailMessage.objects.get(id=message_id[0])
            try:
                header = message.headers.get(name='From')
            except:
                pass
            else:
                email_address = email.utils.parseaddr(header.value)[1]
                if email_address == message.account.email.email_address:
                    message.sent_from_account = True
                    message.save()
            if settings.SOUTH_VERBOSITY > 0:
                i += 1
                print_progress(i, total_messages)

        if total_messages is 0:
            print ' - Nothing to migrate'

    def backwards(self, orm):
        """
        No need to do anything.
        """
        pass

    models = {
        u'accounts.account': {
            'Meta': {'ordering': "['name']", 'object_name': 'Account'},
            'addresses': ('lily.utils.models.fields.AddressFormSetField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'bankaccountnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'bic': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cocnumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'company_size': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('lily.utils.models.fields.EmailAddressFormSetField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'flatname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'legalentity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone_numbers': ('lily.utils.models.fields.PhoneNumberFormSetField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'taxnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contacts.contact': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Contact'},
            'addresses': ('lily.utils.models.fields.AddressFormSetField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('lily.utils.models.fields.EmailAddressFormSetField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'phone_numbers': ('lily.utils.models.fields.PhoneNumberFormSetField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
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
        'email.emailaccount': {
            'Meta': {'ordering': "['email__email_address']", 'object_name': 'EmailAccount', '_ormbases': [u'messaging.MessagesAccount']},
            'auth_ok': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email'", 'unique': 'True', 'to': "orm['utils.EmailAddress']"}),
            'folders': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'from_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_sync_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            u'messagesaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['messaging.MessagesAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django_fields.fields.EncryptedCharField', [], {'max_length': '558', 'block_type': "'MODE_CBC'", 'cipher': "'AES'"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_accounts'", 'to': "orm['email.EmailProvider']"}),
            'signature': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'username': ('django_fields.fields.EncryptedCharField', [], {'max_length': '558', 'block_type': "'MODE_CBC'", 'cipher': "'AES'"})
        },
        'email.emailaddressheader': {
            'Meta': {'object_name': 'EmailAddressHeader'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email.EmailMessage']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
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
            'Meta': {'unique_together': "(('uid', 'folder_name', 'account'),)", 'object_name': 'EmailMessage', '_ormbases': [u'messaging.Message']},
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
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_messaging.messagesaccount_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'shared_with': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'user_group': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'messages_accounts'", 'symmetrical': 'False', 'to': u"orm['users.CustomUser']"})
        },
        u'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'users.customuser': {
            'Meta': {'ordering': "['contact']", 'object_name': 'CustomUser', '_ormbases': [u'auth.User']},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['accounts.Account']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['contacts.Contact']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'utils.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'utils.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'utils.historylistitem': {
            'Meta': {'object_name': 'HistoryListItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_utils.historylistitem_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sort_by_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'utils.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
        },
        'utils.socialmedia': {
            'Meta': {'object_name': 'SocialMedia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['email']
    symmetrical = True
