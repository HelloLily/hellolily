# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'TaskStatus', fields ['status']
        db.create_index(u'taskmonitor_taskstatus', ['status'])

        # Adding index on 'TaskStatus', fields ['task_id']
        db.create_index(u'taskmonitor_taskstatus', ['task_id'])


    def backwards(self, orm):
        # Removing index on 'TaskStatus', fields ['task_id']
        db.delete_index(u'taskmonitor_taskstatus', ['task_id'])

        # Removing index on 'TaskStatus', fields ['status']
        db.delete_index(u'taskmonitor_taskstatus', ['status'])


    models = {
        'taskmonitor.taskstatus': {
            'Meta': {'object_name': 'TaskStatus'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signature': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '20', 'db_index': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['taskmonitor']