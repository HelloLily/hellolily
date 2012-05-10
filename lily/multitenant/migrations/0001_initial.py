# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TenantModel'
        db.create_table('multitenant_tenantmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('multitenant', ['TenantModel'])

    def backwards(self, orm):
        # Deleting model 'TenantModel'
        db.delete_table('multitenant_tenantmodel')

    models = {
        'multitenant.tenantmodel': {
            'Meta': {'object_name': 'TenantModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['multitenant']