# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Address.tenant'
        db.add_column('utils_address', 'tenant',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['multitenant.Tenant']),
                      keep_default=False)

        # Adding field 'EmailAddress.tenant'
        db.add_column('utils_emailaddress', 'tenant',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['multitenant.Tenant']),
                      keep_default=False)

        # Adding field 'SocialMedia.tenant'
        db.add_column('utils_socialmedia', 'tenant',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['multitenant.Tenant']),
                      keep_default=False)

        # Adding field 'PhoneNumber.tenant'
        db.add_column('utils_phonenumber', 'tenant',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['multitenant.Tenant']),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Address.tenant'
        db.delete_column('utils_address', 'tenant_id')

        # Deleting field 'EmailAddress.tenant'
        db.delete_column('utils_emailaddress', 'tenant_id')

        # Deleting field 'SocialMedia.tenant'
        db.delete_column('utils_socialmedia', 'tenant_id')

        # Deleting field 'PhoneNumber.tenant'
        db.delete_column('utils_phonenumber', 'tenant_id')

    models = {
        'multitenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'utils.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multitenant.Tenant']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'utils.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multitenant.Tenant']"})
        },
        'utils.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multitenant.Tenant']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
        },
        'utils.socialmedia': {
            'Meta': {'object_name': 'SocialMedia'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multitenant.Tenant']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'utils.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multitenant.Tenant']"})
        }
    }

    complete_apps = ['utils']