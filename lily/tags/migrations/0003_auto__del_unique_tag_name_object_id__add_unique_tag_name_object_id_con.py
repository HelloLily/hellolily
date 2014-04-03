# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Tag', fields ['name', 'object_id']
        db.delete_unique('tags_tag', ['name', 'object_id'])

        # Adding unique constraint on 'Tag', fields ['name', 'object_id', 'content_type']
        db.create_unique('tags_tag', ['name', 'object_id', 'content_type_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Tag', fields ['name', 'object_id', 'content_type']
        db.delete_unique('tags_tag', ['name', 'object_id', 'content_type_id'])

        # Adding unique constraint on 'Tag', fields ['name', 'object_id']
        db.create_unique('tags_tag', ['name', 'object_id'])


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tags.tag': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'object_id', 'content_type'),)", 'object_name': 'Tag'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['tags']