# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PhoneNumber'
        db.create_table('utils_phonenumber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_input', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('type', self.gf('django.db.models.fields.CharField')(default='work', max_length=15)),
            ('other_type', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=10)),
        ))
        db.send_create_signal('utils', ['PhoneNumber'])

        # Adding model 'SocialMedia'
        db.create_table('utils_socialmedia', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('other_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('profile_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('utils', ['SocialMedia'])

        # Adding model 'Address'
        db.create_table('utils_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('street_number', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('complement', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state_province', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('utils', ['Address'])

        # Adding model 'EmailAddress'
        db.create_table('utils_emailaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('is_primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=50)),
        ))
        db.send_create_signal('utils', ['EmailAddress'])

        # Adding model 'Tag'
        db.create_table('utils_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('utils', ['Tag'])

    def backwards(self, orm):
        # Deleting model 'PhoneNumber'
        db.delete_table('utils_phonenumber')

        # Deleting model 'SocialMedia'
        db.delete_table('utils_socialmedia')

        # Deleting model 'Address'
        db.delete_table('utils_address')

        # Deleting model 'EmailAddress'
        db.delete_table('utils_emailaddress')

        # Deleting model 'Tag'
        db.delete_table('utils_tag')

    models = {
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
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'utils.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'})
        },
        'utils.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
        },
        'utils.socialmedia': {
            'Meta': {'object_name': 'SocialMedia'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'utils.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['utils']