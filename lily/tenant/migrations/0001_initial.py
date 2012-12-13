# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    needed_by = (
         ('accounts', '0001_initial'),
         ('cases', '0001_initial'),
         ('contacts', '0001_initial'),
         ('messages.email', '0001_initial'),
         ('tags', '0001_initial'),
         ('users', '0001_initial'),
         ('utils', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'Tenant'
        db.create_table('tenant_tenant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('tenant', ['Tenant'])

    def backwards(self, orm):
        # Deleting model 'Tenant'
        db.delete_table('tenant_tenant')

    models = {
        'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['tenant']
