# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
        ('socialmedia', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='addresses',
            field=models.ManyToManyField(to='utils.Address', verbose_name='list of addresses', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='assigned_to',
            field=models.ForeignKey(verbose_name='assigned to', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='email_addresses',
            field=models.ManyToManyField(to='utils.EmailAddress', verbose_name='list of e-mail addresses', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='phone_numbers',
            field=models.ManyToManyField(to='utils.PhoneNumber', verbose_name='list of phone numbers', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='social_media',
            field=models.ManyToManyField(
                to='socialmedia.SocialMedia',
                verbose_name='list of social media',
                blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
    ]
