# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import Count


def set_correct_status(apps, schema_editor):
    """
    Some deals had incorrect status of new business.

    This migration tries to fix that for two cases:
     - When an account only has one deal.
     - When an account has no deal with 'new business' status at all.
    """
    deal_cls = apps.get_model('deals', 'Deal')

    # All accounts with one deal -> set deal to 'new business'.
    account_id_list = deal_cls.objects.values('account').annotate(ac_count=Count('account')).filter(ac_count=1).values_list('account_id', flat=True)
    deal_cls.objects.filter(account_id__in=account_id_list).update(new_business=True)

    # All accounts with multiple deals, but none 'new business' -> set first deal to 'new business'.
    account_id_list = deal_cls.objects.values('account').annotate(ac_count=Count('account')).exclude(ac_count=1).values_list('account_id', flat=True)
    for account_id in account_id_list:
        # Fetch list with deals and check if any of them is new business.
        if not deal_cls.objects.filter(account_id=account_id, new_business=True).exists():
            # deal with status new business doesn't exist, so set first deal to 'new business'.
            deal = deal_cls.objects.filter(account_id=account_id).order_by('created').first()
            deal.new_business = True
            deal.save()


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0007_auto_20150902_1543'),
    ]

    operations = [
        migrations.RunPython(set_correct_status, backwards_noop),
    ]
