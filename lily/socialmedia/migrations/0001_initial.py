# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    needed_by = (
        ("utils", "0010_auto__move_socialmedia"),
    )

    def forwards(self, orm):
        db.rename_table('utils_socialmedia', 'socialmedia_socialmedia')

        if not db.dry_run:
            # For permissions to work properly after migrating
            orm['contenttypes.contenttype'].objects.filter(app_label='utils', model='socialmedia').update(app_label='socialmedia')

            # Fix foreign key for accounts
            db.delete_foreign_key('accounts_account_social_media', 'socialmedia_id')
            sql = db.foreign_key_sql('accounts_account_social_media', 'socialmedia_id', 'socialmedia_socialmedia', 'id')
            db.execute(sql)

            # Fix foreign key for contacts
            db.delete_foreign_key('contacts_contact_social_media', 'socialmedia_id')
            sql = db.foreign_key_sql('contacts_contact_social_media', 'socialmedia_id', 'socialmedia_socialmedia', 'id')
            db.execute(sql)

    def backwards(self, orm):
        pass

    models = {
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
        }
    }

    complete_apps = ['contenttypes', 'socialmedia']
