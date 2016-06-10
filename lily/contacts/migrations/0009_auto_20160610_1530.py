# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.contacts.models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0008_auto_20160603_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='first_name',
            field=models.CharField(default=b'', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='gender',
            field=models.IntegerField(default=2, choices=[(0, 'Male'), (1, 'Female'), (2, 'Unknown/Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='last_name',
            field=models.CharField(default=b'', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='picture',
            field=models.ImageField(upload_to=lily.contacts.models.get_contact_picture_upload_path, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='preposition',
            field=models.CharField(default=b'', max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='salutation',
            field=models.IntegerField(default=1, choices=[(0, 'Formal'), (1, 'Informal')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='title',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='department',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='email_addresses',
            field=models.ManyToManyField(to='utils.EmailAddress'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='manager',
            field=models.ForeignKey(related_name='manager', blank=True, to='contacts.Contact', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='phone_numbers',
            field=models.ManyToManyField(to='utils.PhoneNumber'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='title',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
