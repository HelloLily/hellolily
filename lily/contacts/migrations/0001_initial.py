# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    needed_by = (
        ('cases', '0001_initial'),
        ('users', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'Contact'
        db.create_table('contacts_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('preposition', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('salutation', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('contacts', ['Contact'])

        # Adding M2M table for field phone_numbers on 'Contact'
        db.create_table('contacts_contact_phone_numbers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm['contacts.contact'], null=False)),
            ('phonenumber', models.ForeignKey(orm['utils.phonenumber'], null=False))
        ))
        db.create_unique('contacts_contact_phone_numbers', ['contact_id', 'phonenumber_id'])

        # Adding M2M table for field social_media on 'Contact'
        db.create_table('contacts_contact_social_media', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm['contacts.contact'], null=False)),
            ('socialmedia', models.ForeignKey(orm['utils.socialmedia'], null=False))
        ))
        db.create_unique('contacts_contact_social_media', ['contact_id', 'socialmedia_id'])

        # Adding M2M table for field addresses on 'Contact'
        db.create_table('contacts_contact_addresses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm['contacts.contact'], null=False)),
            ('address', models.ForeignKey(orm['utils.address'], null=False))
        ))
        db.create_unique('contacts_contact_addresses', ['contact_id', 'address_id'])

        # Adding M2M table for field email_addresses on 'Contact'
        db.create_table('contacts_contact_email_addresses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm['contacts.contact'], null=False)),
            ('emailaddress', models.ForeignKey(orm['utils.emailaddress'], null=False))
        ))
        db.create_unique('contacts_contact_email_addresses', ['contact_id', 'emailaddress_id'])

        # Adding model 'Function'
        db.create_table('contacts_function', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='functions', to=orm['accounts.Account'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='functions', to=orm['contacts.Contact'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='manager', null=True, to=orm['contacts.Contact'])),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('contacts', ['Function'])

        # Adding M2M table for field phone_numbers on 'Function'
        db.create_table('contacts_function_phone_numbers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('function', models.ForeignKey(orm['contacts.function'], null=False)),
            ('phonenumber', models.ForeignKey(orm['utils.phonenumber'], null=False))
        ))
        db.create_unique('contacts_function_phone_numbers', ['function_id', 'phonenumber_id'])

        # Adding M2M table for field email_addresses on 'Function'
        db.create_table('contacts_function_email_addresses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('function', models.ForeignKey(orm['contacts.function'], null=False)),
            ('emailaddress', models.ForeignKey(orm['utils.emailaddress'], null=False))
        ))
        db.create_unique('contacts_function_email_addresses', ['function_id', 'emailaddress_id'])

    def backwards(self, orm):
        # Deleting model 'Contact'
        db.delete_table('contacts_contact')

        # Removing M2M table for field phone_numbers on 'Contact'
        db.delete_table('contacts_contact_phone_numbers')

        # Removing M2M table for field social_media on 'Contact'
        db.delete_table('contacts_contact_social_media')

        # Removing M2M table for field addresses on 'Contact'
        db.delete_table('contacts_contact_addresses')

        # Removing M2M table for field email_addresses on 'Contact'
        db.delete_table('contacts_contact_email_addresses')

        # Deleting model 'Function'
        db.delete_table('contacts_function')

        # Removing M2M table for field phone_numbers on 'Function'
        db.delete_table('contacts_function_phone_numbers')

        # Removing M2M table for field email_addresses on 'Function'
        db.delete_table('contacts_function_email_addresses')

    models = {
        'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False'}),
            'bankaccountnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'bic': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cocnumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'company_size': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False'}),
            'flatname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'legalentity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.SocialMedia']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'contacts.function': {
            'Meta': {'object_name': 'Function'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['accounts.Account']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['contacts.Contact']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manager'", 'null': 'True', 'to': "orm['contacts.Contact']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'users.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Account']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts.Contact']"}),
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
        },
        'utils.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tenant.Tenant']", 'blank': 'True'})
        }
    }

    complete_apps = ['contacts']