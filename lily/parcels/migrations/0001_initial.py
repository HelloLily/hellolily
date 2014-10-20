# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Parcel'
        db.create_table(u'parcels_parcel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('provider', self.gf('django.db.models.fields.IntegerField')(default=[0])),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'parcels', ['Parcel'])


    def backwards(self, orm):
        # Deleting model 'Parcel'
        db.delete_table(u'parcels_parcel')


    models = {
        u'parcels.parcel': {
            'Meta': {'object_name': 'Parcel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'provider': ('django.db.models.fields.IntegerField', [], {'default': '[0]'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        u'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['parcels']