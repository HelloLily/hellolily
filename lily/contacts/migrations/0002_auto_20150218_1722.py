# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
        ('socialmedia', '0001_initial'),
        ('tenant', '0001_initial'),
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='function',
            name='email_addresses',
            field=models.ManyToManyField(to='utils.EmailAddress', verbose_name='list of email addresses'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='function',
            name='manager',
            field=models.ForeignKey(
                related_name='manager',
                verbose_name='manager',
                blank=True,
                to='contacts.Contact',
                null=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='function',
            name='phone_numbers',
            field=models.ManyToManyField(to='utils.PhoneNumber', verbose_name='list of phone numbers'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='function',
            unique_together=set([('account', 'contact')]),
        ),
        migrations.AddField(
            model_name='contact',
            name='addresses',
            field=models.ManyToManyField(to='utils.Address', verbose_name='list of addresses', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='email_addresses',
            field=models.ManyToManyField(to='utils.EmailAddress', verbose_name='list of e-mail addresses', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='phone_numbers',
            field=models.ManyToManyField(to='utils.PhoneNumber', verbose_name='list of phone numbers', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='social_media',
            field=models.ManyToManyField(
                to='socialmedia.SocialMedia',
                verbose_name='list of social media',
                blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
    ]
