# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fix_multiple_default_templates(apps, schema_editor):
    # Some users have more than 1 default template.
    # This shouldn't be possible, make sure is will be just 1.
    User = apps.get_model('users', 'LilyUser')
    DefaultEmailTemplate = apps.get_model('email', 'DefaultEmailTemplate')

    print('\nFixing default template for the following users:')
    for user in User.objects.all():
        templates = DefaultEmailTemplate.objects.filter(user=user.pk).order_by('id')
        if templates.count() > 1:
            # User has more than one default template.
            # Best guess would be that the user prefers the last set template to be the default.
            # So remove all except the last one.
            template_to_keep = templates.last()
            templates.exclude(id=template_to_keep.id).delete()

            print('%d:\t%s' % (user.pk, user.email))


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0012_auto_20160715_1423'),
    ]

    operations = [
        migrations.RunPython(fix_multiple_default_templates),
    ]
