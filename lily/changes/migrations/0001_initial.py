# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0004_tenant_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=10, choices=[(b'get', b'GET'), (b'post', b'POST'), (b'put', b'PUT'), (b'patch', b'PATCH')])),
                ('data', models.TextField()),
                ('object_id', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
                ('user', models.ForeignKey(related_name='object_changes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
