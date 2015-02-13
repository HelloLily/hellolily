# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DefaultEmailTemplate', fields ['user', 'account']
        db.delete_unique(u'email_defaultemailtemplate', ['user_id', 'account_id'])

        # Removing unique constraint on 'EmailMessage', fields ['uid', 'folder_name', 'account']
        db.delete_unique(u'email_emailmessage', ['uid', 'folder_name', 'account_id'])

        # Deleting model 'EmailTemplateAttachment'
        db.delete_table(u'email_emailtemplateattachment')

        # Deleting model 'EmailHeader'
        db.delete_table(u'email_emailheader')

        # Deleting model 'EmailAddressHeader'
        db.delete_table(u'email_emailaddressheader')

        # Deleting model 'ActionStep'
        db.delete_table(u'email_actionstep')

        # Deleting model 'EmailLabel'
        db.delete_table(u'email_emaillabel')

        # Deleting model 'EmailAccount'
        db.delete_table(u'email_emailaccount')

        # Deleting model 'EmailAttachment'
        db.delete_table(u'email_emailattachment')

        # Deleting model 'EmailMessage'
        db.delete_table(u'email_emailmessage')

        # Deleting model 'EmailDraft'
        db.delete_table(u'email_emaildraft')

        # Deleting model 'EmailAddress'
        db.delete_table(u'email_emailaddress')

        # Deleting model 'EmailOutboxMessage'
        db.delete_table(u'email_emailoutboxmessage')

        # Deleting model 'EmailTemplate'
        db.delete_table(u'email_emailtemplate')

        # Deleting model 'EmailOutboxAttachment'
        db.delete_table(u'email_emailoutboxattachment')

        # Deleting model 'EmailProvider'
        db.delete_table(u'email_emailprovider')

        # Deleting model 'DefaultEmailTemplate'
        db.delete_table(u'email_defaultemailtemplate')


    def backwards(self, orm):
        # Adding index on 'EmailMessage', fields ['folder_name', 'account']
        db.create_index(u'email_emailmessage', ['folder_name', 'account_id'])

        # Adding model 'EmailTemplateAttachment'
        db.create_table(u'email_emailtemplateattachment', (
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['email.EmailTemplate'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('email', ['EmailTemplateAttachment'])

        # Adding model 'EmailHeader'
        db.create_table(u'email_emailheader', (
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='headers', to=orm['email.EmailMessage'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('email', ['EmailHeader'])

        # Adding model 'EmailAddressHeader'
        db.create_table(u'email_emailaddressheader', (
            ('value', self.gf('django.db.models.fields.TextField')(null=True, db_index=True)),
            ('sent_date', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['email.EmailMessage'])),
            ('message_identifier', self.gf('django.db.models.fields.CharField')(blank=True, max_length=255, null=True, db_index=True)),
            ('email_address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['email.EmailAddress'], null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
        ))
        db.send_create_signal('email', ['EmailAddressHeader'])

        # Adding model 'ActionStep'
        db.create_table(u'email_actionstep', (
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['email.EmailMessage'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
        ))
        db.send_create_signal('email', ['ActionStep'])

        # Adding model 'EmailLabel'
        db.create_table(u'email_emaillabel', (
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', to=orm['email.EmailMessage'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('email', ['EmailLabel'])

        # Adding model 'EmailAccount'
        db.create_table(u'email_emailaccount', (
            ('folders', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('username', self.gf('django_fields.fields.EncryptedCharField')(max_length=558, block_type='MODE_CBC', cipher='AES')),
            ('from_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django_fields.fields.EncryptedCharField')(max_length=558, block_type='MODE_CBC', cipher='AES')),
            ('auth_ok', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('last_sync_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(related_name='email_accounts', to=orm['email.EmailProvider'])),
            (u'messagesaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['messaging.MessagesAccount'], unique=True, primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
        ))
        db.send_create_signal('email', ['EmailAccount'])

        # Adding model 'EmailAttachment'
        db.create_table(u'email_emailattachment', (
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('inline', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['email.EmailMessage'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('email', ['EmailAttachment'])

        # Adding model 'EmailMessage'
        db.create_table(u'email_emailmessage', (
            ('uid', self.gf('django.db.models.fields.IntegerField')()),
            ('body_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('message_identifier', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sent_from_account', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('folder_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            (u'message_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['messaging.Message'], unique=True, primary_key=True)),
            ('is_private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('folder_identifier', self.gf('django.db.models.fields.CharField')(blank=True, max_length=255, null=True, db_index=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['email.EmailAccount'])),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('flags', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
        ))
        db.send_create_signal('email', ['EmailMessage'])

        # Adding unique constraint on 'EmailMessage', fields ['uid', 'folder_name', 'account']
        db.create_unique(u'email_emailmessage', ['uid', 'folder_name', 'account_id'])

        # Adding model 'EmailDraft'
        db.create_table(u'email_emaildraft', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('send_to_bcc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('send_to_cc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('send_to_normal', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('send_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='drafts', to=orm['email.EmailAccount'])),
            ('body_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('email', ['EmailDraft'])

        # Adding model 'EmailAddress'
        db.create_table(u'email_emailaddress', (
            ('email_address', self.gf('django.db.models.fields.CharField')(max_length=1000, db_index=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('email', ['EmailAddress'])

        # Adding model 'EmailOutboxMessage'
        db.create_table(u'email_emailoutboxmessage', (
            ('body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('to', self.gf('django.db.models.fields.TextField')()),
            ('send_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outbox_messages', to=orm['email.EmailAccount'])),
            ('bcc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mapped_attachments', self.gf('django.db.models.fields.IntegerField')()),
            ('headers', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('email', ['EmailOutboxMessage'])

        # Adding model 'EmailTemplate'
        db.create_table(u'email_emailtemplate', (
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('body_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('email', ['EmailTemplate'])

        # Adding model 'EmailOutboxAttachment'
        db.create_table(u'email_emailoutboxattachment', (
            ('email_outbox_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['email.EmailOutboxMessage'])),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('inline', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], blank=True)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('email', ['EmailOutboxAttachment'])

        # Adding model 'EmailProvider'
        db.create_table(u'email_emailprovider', (
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tenant.Tenant'], null=True, blank=True)),
            ('imap_port', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('imap_host', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('smtp_port', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('smtp_host', self.gf('django.db.models.fields.CharField')(max_length=32)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('imap_ssl', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('smtp_ssl', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('email', ['EmailProvider'])

        # Adding model 'DefaultEmailTemplate'
        db.create_table(u'email_defaultemailtemplate', (
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_templates', to=orm['email.EmailAccount'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_templates', to=orm['email.EmailTemplate'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_templates', to=orm['users.LilyUser'])),
        ))
        db.send_create_signal('email', ['DefaultEmailTemplate'])

        # Adding unique constraint on 'DefaultEmailTemplate', fields ['user', 'account']
        db.create_unique(u'email_defaultemailtemplate', ['user_id', 'account_id'])


    models = {

    }

    complete_apps = ['email']
