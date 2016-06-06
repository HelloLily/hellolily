# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def to_lower_case(apps, schema_editor):
    Tag = apps.get_model('tags', 'Tag')

    tags = Tag.objects.all()
    # Loop reversed so tags can also be deleted.
    for tag in reversed(tags):
        tag.update_modified = False

        cnt = Tag.objects.filter(
            name=tag.name.lower,
            object_id=tag.object_id,
            content_type_id=tag.content_type_id).count()
        if cnt > 0:
            # After converting to lowercase the new tag would yield in a
            # IntegrityError: duplicate key value violates unique constraint
            # so this tag is redundant.
            Tag.objects.filter(id=tag.id).delete()
        else:
            tag.name = tag.name.lower()
            tag.save()


def delete_tags(apps, schema_editor):
    # The following list is based on manually processing of the following management commando:
    # docker-compose run web python manage.py tags
    delete = [
        "facturen", "factuur", "ferdytesttag", "testtag", "fritzfox", "frtizbox", "testtagsjoerd", "[voizes]", "vozies"
    ]

    Tag = apps.get_model('tags', 'Tag')

    tags = Tag.objects.all()
    # Loop reversed so tags can also be deleted.
    for tag in reversed(tags):
        if tag.name in delete:
            Tag.objects.filter(id=tag.id).delete()


def tag_rewrite(apps, schema_editor):
    # The following dictonary is based on manually processing of the following management commando:
    # docker-compose run web python manage.py tags
    rename = {
        "303": "spa303", "504g": "spa504g", "spa 504g": "spa504g", "514": "spa514",
        "accessattempt": "too many access attempts", "geluidskwaliteits": "audiokwaliteit",
        "audioproblomen": "audioproblemen", "belgië": "belgie", "belgroep": "belgroepen", "belpan": "belplan",
        "beschikbaarheid": "bereikbaarheid", "callwaiting": "call waiting", "cisco spa504g": "spa504g",
        "doorschakeling": "doorschakelen", "schakelen": "doorschakelen", "e-mail": "email", "facturen": "facturatie",
        "factuur": "facturatie", "firmareupdate": "firmware update", "fritzfox": "fritzbox", "frtizbox": "fritzbox",
        "kapoet": "kapot", "klikenbel": "klik en bel", "niet bereikbaar": "onbereikbaar", "niewsbrief": "nieuwsbrief",
        "opzeggen": "opzegging", "piep": "pieptoon", "porteren": "portering", "portforward": "portforwarding",
        "portforwardings": "portforwarding", "ringtijd": "rinkeltijd", "servicenumber": "servicenummer",
        "tp link": "tp-link", "uitgaande naam (cli)": "uitgaand cli", "verbroken verbinding": "verbrekende verbinding",
        "wegvallende verbinding": "verbrekende verbinding", "voipaccount": "voip account", "[voizes]": "voizes",
        "vozies": "voizes", "voys-app": "voys app", "webhook": "webhooks", "wegvallende spraak": "wegvallende audio",
        "xlite": "x-lite",
    }

    # Update dictonary with specific suggestions from LILY-1228.
    rename.update({
        "dubbelnat": "dubbel nat", "configuratie": "config", "deurtintercom": "deurtelefoon",
        "gebruikers": "gebruiker",
    })

    Tag = apps.get_model('tags', 'Tag')

    tags = Tag.objects.all()
    # Loop reversed so tags can also be deleted.
    for tag in reversed(tags):
        tag.update_modified = False

        if tag.name in rename:
            cnt = Tag.objects.filter(
                name=rename[tag.name],
                object_id=tag.object_id,
                content_type_id=tag.content_type_id).count()
            if cnt > 0:
                # After rename the new tag would yield in a
                # IntegrityError: duplicate key value violates unique constraint
                # so this tag is redundant.
                Tag.objects.filter(id=tag.id).delete()
            else:
                tag.name = rename[tag.name]
                tag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0002_auto_20151006_0941'),
    ]

    operations = [
        migrations.RunPython(to_lower_case),
        migrations.RunPython(delete_tags),
        migrations.RunPython(tag_rewrite),
    ]
