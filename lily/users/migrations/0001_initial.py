# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('socialmedia', '0001_initial'),
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LilyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=45, verbose_name='first name')),
                ('preposition', models.CharField(max_length=100, verbose_name='preposition', blank=True)),
                ('last_name', models.CharField(max_length=45, verbose_name='last name')),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=40, verbose_name='phone number', blank=True)),
                ('language', models.CharField(default=b'en', max_length=3, verbose_name='language', choices=[(b'nl', b'Dutch'), (b'en', b'English')])),
                ('timezone', timezone_field.fields.TimeZoneField(default=b'Europe/Amsterdam')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('social_media', models.ManyToManyField(to='socialmedia.SocialMedia', verbose_name='list of social media', blank=True)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'permissions': (('send_invitation', 'Can send invitations to invite new users'),),
            },
            bases=(models.Model,),
        ),
    ]
