# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.contrib.contenttypes.models import ContentType

class Migration(DataMigration):

    depends_on = (
        ('utils', '0003_auto__add_historylistitem'),
    )

    def forwards(self, orm):
        # Start transaction
        db.start_transaction()

        # Rename the table for data backup
        db.rename_table('notes_note', 'notes_note_old')

        # create the table notes_note with the right layout
        db.create_table('notes_note', (
            ('historylistitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['utils.HistoryListItem'], unique=True, primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.CustomUser'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('notes', ['Note'])

        # Get all notes from the old table
        old_notes = db.execute('SELECT * FROM notes_note_old')

        # Delete notes_note_old
        db.delete_table('notes_note_old')

        # Commit transaction
        db.commit_transaction()

        # Get the content type id for the Note model
        from django.contrib.contenttypes.management import update_all_contenttypes
        update_all_contenttypes()
        ctype_id = ContentType.objects.get(app_label='notes', model='note').pk

        # Create new notes
        for note in old_notes:
            created = note[1]
            modified = note[2]
            deleted = note[3]
            is_deleted = note[4]
            content = note[5]
            author_id = note[6]
            content_type_id = note[7]
            object_id = note[8]

            orm.Note.objects.create(
                created=created,
                modified=modified,
                deleted=deleted,
                is_deleted=is_deleted,
                content=content,
                author_id=author_id,
                content_type_id=content_type_id,
                object_id=object_id,
                polymorphic_ctype_id=ctype_id
            )


    def backwards(self, orm):
        # Start transaction
        db.start_transaction()

        # Remove constraints
        db.delete_foreign_key('notes_note', 'author_id')
        db.delete_foreign_key('notes_note', 'content_type_id')
        db.delete_foreign_key('notes_note', 'historylistitem_ptr_id')

        # Delete indexes
        db.delete_index('notes_note', ['author_id'])
        db.delete_index('notes_note', ['content_type_id'])

        # Rename the note table
        db.rename_table('notes_note', 'notes_note_new')

        # Create the new note table
        db.create_table('notes_note', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('note', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.CustomUser'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('notes', ['Note'])

        # Get all notes from the new table
        new_notes = db.execute('SELECT * FROM notes_note_new')

        # Delete notes_note_new
        db.delete_table('notes_note_new')

        # Commit transaction
        db.commit_transaction()

        # Recreate old notes
        for note in new_notes:
            created = note[1]
            modified = note[2]
            deleted = note[3]
            is_deleted = note[4]
            text = note[5]
            author_id = note[6]
            content_type_id = note[7]
            object_id = note[8]

            query = "INSERT INTO notes_note VALUES (DEFAULT, '%s', '%s', '%s', %s, '%s', %s, %s, %s)" % (
                created,
                modified,
                deleted,
                is_deleted,
                text,
                author_id,
                content_type_id,
                object_id
            )
            db.execute(query)

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
        'notes.note': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Note', '_ormbases': ['utils.HistoryListItem']},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.CustomUser']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'historylistitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['utils.HistoryListItem']", 'unique': 'True', 'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
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
        'utils.historylistitem': {
            'Meta': {'object_name': 'HistoryListItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_utils.historylistitem_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"})
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

    complete_apps = ['notes']
    symmetrical = True
