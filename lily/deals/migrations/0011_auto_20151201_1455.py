# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import migrations
from lily.deals import models
from lily.tenant.models import Tenant


def update_next_step(apps, schema_editor):
    open_stage = models.Deal.OPEN_STAGE
    pending_stage = models.Deal.PENDING_STAGE
    called_stage = models.Deal.CALLED_STAGE
    emailed_stage = models.Deal.EMAILED_STAGE
    won_stage = models.Deal.WON_STAGE

    Tenant = apps.get_model('tenant', 'Tenant')
    Deal = apps.get_model('deals', 'Deal')
    DealNextStep = apps.get_model('deals', 'DealNextStep')

    tenants = Tenant.objects.all()

    for tenant in tenants:
        deals = Deal.objects.filter(tenant=tenant)
        if deals:
            deal_next_steps = DealNextStep.objects.filter(tenant=tenant)

            if deal_next_steps:
                try:
                    next_step_follow_up = deal_next_steps.get(name='Follow up')
                    next_step_request_feedback = deal_next_steps.get(name='Feedback request')
                    next_step_none = deal_next_steps.get(name='None')
                except DealNextStep.DoesNotExist:
                    pass
                else:
                    for deal in deals:
                        if not deal.next_step:
                            if deal.stage == open_stage:
                                deal.next_step = next_step_follow_up
                                deal.next_step_date = deal.modified + datetime.timedelta(days=2)
                            elif deal.stage == pending_stage or deal.stage == called_stage or deal.stage == emailed_stage:
                                deal.next_step = next_step_follow_up
                                deal.next_step_date = deal.modified + datetime.timedelta(days=7)
                            elif deal.stage == won_stage and not deal.feedback_form_sent:
                                deal.next_step = next_step_request_feedback
                                deal.next_step_date = deal.modified + datetime.timedelta(days=30)
                            elif deal.stage == won_stage and deal.feedback_form_sent:
                                deal.next_step = next_step_none
                                deal.next_step_date = None

                            deal.save()


def clear_next_step(apps, schema_editor):
    Deal = apps.get_model('deals', 'Deal')
    deals = Deal.objects.all()

    for deal in deals:
        deal.next_step = None
        deal.next_step_date = ''


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0010_auto_20151127_1146'),
        ('tenant', '0002_tenant_name'),
    ]

    operations = [
        migrations.RunPython(update_next_step, reverse_code=clear_next_step)
    ]
