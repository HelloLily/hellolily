# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Account.assigned_to'
        db.add_column(u'accounts_account', 'assigned_to',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.LilyUser'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Account.assigned_to'
        db.delete_column(u'accounts_account', 'assigned_to_id')


    models = {
        u'accounts.account': {
            'Meta': {'ordering': "['name']", 'object_name': 'Account'},
            'addresses': ('lily.utils.models.fields.AddressFormSetField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.LilyUser']", 'null': 'True', 'blank': 'True'}),
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
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['socialmedia.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'taxnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        u'accounts.website': {
            'Meta': {'object_name': 'Website'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'websites'", 'to': u"orm['accounts.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '255'})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'socialmedia.socialmedia': {
            'Meta': {'object_name': 'SocialMedia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
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
        'utils.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
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
        'utils.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
        }
    }

    complete_apps = ['accounts']