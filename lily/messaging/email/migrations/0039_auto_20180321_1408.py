# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-21 14:08
from __future__ import unicode_literals

from django.db import migrations, models, transaction, connection
from django.conf import settings


def set_boolean_field(apps, schema_editor):
    i = 0
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("""
            DECLARE mycursor CURSOR FOR
            SELECT id
            FROM email_emailmessage
        """)
        while True:
            print "Now processing %s" % (i*1000)
            cursor.execute("FETCH 1000 FROM mycursor")
            chunk = cursor.fetchall()
            if not chunk:
                break
            for row in chunk:
                id = row[0]
                process_row(id)

            i += 1

def process_row(id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT count(1)
              FROM email_emaillabel
             INNER JOIN email_emailmessage_labels
                ON (email_emaillabel.id = email_emailmessage_labels.emaillabel_id)
             WHERE (email_emailmessage_labels.emailmessage_id = %s AND email_emaillabel.label_id = %s)
        """, [id, settings.GMAIL_LABEL_INBOX])

        row = cursor.fetchone()
        is_inbox = True if row[0] else False

        cursor.execute("""
            SELECT count(1)
              FROM email_emaillabel
             INNER JOIN email_emailmessage_labels
                ON (email_emaillabel.id = email_emailmessage_labels.emaillabel_id)
             WHERE (email_emailmessage_labels.emailmessage_id = %s AND email_emaillabel.label_id = %s)
        """, [id, settings.GMAIL_LABEL_SPAM])

        row = cursor.fetchone()
        is_spam = True if row[0] else False

        cursor.execute("""
            SELECT count(1)
              FROM email_emaillabel
             INNER JOIN email_emailmessage_labels
                ON (email_emaillabel.id = email_emailmessage_labels.emaillabel_id)
             WHERE (email_emailmessage_labels.emailmessage_id = %s AND email_emaillabel.label_id = %s)
        """, [id, settings.GMAIL_LABEL_SENT])

        row = cursor.fetchone()
        is_sent = True if row[0] else False

        cursor.execute("""
            SELECT count(1)
              FROM email_emaillabel
             INNER JOIN email_emailmessage_labels
                ON (email_emaillabel.id = email_emailmessage_labels.emaillabel_id)
             WHERE (email_emailmessage_labels.emailmessage_id = %s AND email_emaillabel.label_id = %s)
        """, [id, settings.GMAIL_LABEL_TRASH])

        row = cursor.fetchone()
        is_trashed = True if row[0] else False

        cursor.execute("""
            SELECT count(1)
              FROM email_emaillabel
             INNER JOIN email_emailmessage_labels
                ON (email_emaillabel.id = email_emailmessage_labels.emaillabel_id)
             WHERE (email_emailmessage_labels.emailmessage_id = %s AND email_emaillabel.label_id = %s)
        """, [id, settings.GMAIL_LABEL_DRAFT])

        row = cursor.fetchone()
        is_draft = True if row[0] else False

        cursor.execute("""
            SELECT count(1)
              FROM email_emaillabel
             INNER JOIN email_emailmessage_labels
                ON (email_emaillabel.id = email_emailmessage_labels.emaillabel_id)
             WHERE (email_emailmessage_labels.emailmessage_id = %s AND email_emaillabel.label_id = %s)
        """, [id, settings.GMAIL_LABEL_STAR])

        row = cursor.fetchone()
        is_starred = True if row[0] else False

        cursor.execute("""
            UPDATE email_emailmessage
               SET is_inbox = %s,
                   is_sent = %s,
                   is_trashed = %s,
                   is_spam = %s,
                   is_draft = %s,
                   is_starred = %s
             WHERE email_emailmessage.id = %s
        """, [is_inbox, is_sent, is_trashed, is_spam, is_draft, is_starred, id])

def noop():
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0038_auto_20180321_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailmessage',
            name='is_inbox',
            field=models.NullBooleanField(default=True, db_index=True, verbose_name='Is inbox'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='is_sent',
            field=models.NullBooleanField(default=False, db_index=True, verbose_name='Is sent'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='is_spam',
            field=models.NullBooleanField(default=False, db_index=True, verbose_name='Is spam'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='is_trashed',
            field=models.NullBooleanField(default=False, db_index=True, verbose_name='Is trashed'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='is_draft',
            field=models.NullBooleanField(default=False, db_index=True, verbose_name='Is draft'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='is_starred',
            field=models.NullBooleanField(default=False, db_index=True, verbose_name='Is starred'),
        ),
        migrations.RunPython(set_boolean_field, noop),
    ]
