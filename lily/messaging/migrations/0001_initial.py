# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    needed_by = (
         ('messaging.email', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'MessagesAccount'
        db.create_table('messaging_messagesaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='polymorphic_messages.messagesaccount_set', null=True, to=orm['contenttypes.ContentType'])),
            ('account_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('messaging', ['MessagesAccount'])

        # Adding M2M table for field user_group on 'MessagesAccount'
        db.create_table('messaging_messagesaccount_user_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagesaccount', models.ForeignKey(orm['messaging.messagesaccount'], null=False)),
            ('customuser', models.ForeignKey(orm['users.customuser'], null=False))
        ))
        db.create_unique('messaging_messagesaccount_user_group', ['messagesaccount_id', 'customuser_id'])

        # Adding model 'Message'
        db.create_table('messaging_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='polymorphic_messages.message_set', null=True, to=orm['contenttypes.ContentType'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_seen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['messaging.MessagesAccount'])),
        ))
        db.send_create_signal('messaging', ['Message'])


    def backwards(self, orm):
        # Deleting model 'MessagesAccount'
        db.delete_table('messaging_messagesaccount')

        # Removing M2M table for field user_group on 'MessagesAccount'
        db.delete_table('messaging_messagesaccount_user_group')

        # Deleting model 'Message'
        db.delete_table('messaging_message')


    models = {
        'accounts.account': {
            'Meta': {'ordering': "['name']", 'object_name': 'Account'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'bankaccountnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'bic': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cocnumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'company_size': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'flatname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'legalentity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'taxnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contacts.contact': {
            'Meta': {'object_name': 'Contact'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'messaging.message': {
            'Meta': {'object_name': 'Message'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['messaging.MessagesAccount']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_seen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_messages.message_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'messaging.messagesaccount': {
            'Meta': {'object_name': 'MessagesAccount'},
            'account_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_messages.messagesaccount_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'user_group': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'social_media_accounts'", 'symmetrical': 'False', 'to': "orm['users.CustomUser']"})
        },
        'notes.note': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Note'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.CustomUser']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'tags.tag': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'object_id'),)", 'object_name': 'Tag'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'users.customuser': {
            'Meta': {'ordering': "['contact']", 'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': "orm['accounts.Account']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': "orm['contacts.Contact']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'utils.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'utils.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        },
        'utils.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
        },
        'utils.socialmedia': {
            'Meta': {'object_name': 'SocialMedia'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['messaging']
