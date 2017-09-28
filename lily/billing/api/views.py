import calendar
from datetime import datetime, timedelta

import chargebee
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lily.utils.api.permissions import IsAccountAdmin

from ..models import Plan


class BillingViewSet(ViewSet):
    permission_classes = (IsAccountAdmin, )

    @list_route(methods=['GET', 'PATCH'])
    def subscription(self, request):
        tenant = self.request.user.tenant
        billing = tenant.billing
        customer = billing.get_customer()
        subscription = billing.get_subscription()

        if request.method == 'GET':
            card = billing.get_card()
            plan = None

            if subscription:
                plan = chargebee.Plan.retrieve(subscription.plan_id)
                plan = plan.plan.values

            # Update the plan whenever we fetch the subscription from Chargebee.
            billing.plan = Plan.objects.get(name=subscription.plan_id)
            billing.save()

            invoices = chargebee.Invoice.list({'customer_id[is]': customer.id})

            data = {
                'customer': customer.values,
                'subscription': subscription.values if subscription else None,
                'card': card.values if card else None,
                'plan': plan,
                'invoices': invoices.response,
            }
        elif request.method == 'PATCH':
            plan_id = self.request.data.get('plan_id')

            if not plan_id or plan_id == settings.CHARGEBEE_PRO_TRIAL_PLAN_NAME:
                raise ValidationError(_('Please select a plan'))

            parameters = {
                'customer': {
                    'id': customer.id,
                },
                'subscription': {
                    'plan_id': plan_id,
                },
                'embed': False,
            }

            if subscription:
                if plan_id == settings.CHARGEBEE_FREE_PLAN_NAME:
                    success = False

                    free_plan_parameters = {
                        'plan_id': plan_id,
                    }

                    if billing.trial_started:
                        # Trial has already been started once.
                        # We don't want to set the user back to free plan with trial.
                        free_plan_parameters.update({
                            'trial_end': 0,
                        })

                    # No need to go through the hosted page when changing to free plan.
                    result = chargebee.Subscription.update(subscription.id, free_plan_parameters)

                    if result.subscription.plan_id == plan_id:
                        success = True

                    if success:
                        billing.plan = Plan.objects.get(name=plan_id)
                        billing.save()

                    return Response({'success': success}, content_type='application/json')
                else:
                    user_count = tenant.lilyuser_set.filter(is_active=True).count()

                    parameters.update({
                        'subscription': {
                            'id': subscription.id,
                            'plan_id': plan_id,
                            'plan_quantity': user_count,
                        },
                    })

                    result = chargebee.HostedPage.checkout_existing(parameters)
            else:
                result = chargebee.HostedPage.checkout_new(parameters)

                billing.subscription_id = result.subscription.id
                billing.save()

            data = {
                'url': result.hosted_page.url,
            }

        return Response(data, content_type='application/json')

    @list_route(methods=['GET'])
    def plans(self, request):
        billing = self.request.user.tenant.billing
        current_plan = None
        subscription = billing.get_subscription()

        if subscription:
            current_plan = chargebee.Plan.retrieve(subscription.plan_id).plan.values

        plans = chargebee.Plan.list({'status[is]': 'active', 'id[is_not]': settings.CHARGEBEE_PRO_TRIAL_PLAN_NAME})

        data = {
            'subscription': subscription.values if subscription else None,
            'current_plan': current_plan,
            'plans': plans.response,
        }

        return Response(data, content_type='application/json')

    @list_route(methods=['GET'])
    def update_card(self, request):
        billing = self.request.user.tenant.billing
        customer = billing.get_customer()

        parameters = {
            'customer': {
                'id': customer.id,
            },
            'embed': False,
        }

        result = chargebee.HostedPage.update_payment_method(parameters)

        hosted_page = {
            'url': result.hosted_page.url,
        }

        return Response(hosted_page, content_type='application/json')

    @list_route(methods=['POST'])
    def download_invoice(self, request):
        result = chargebee.Invoice.pdf(self.request.data.get('invoice_id'))

        return Response({'url': result.download.download_url}, content_type='application/json')

    @list_route(methods=['GET'])
    def cancel(self, request):
        billing = self.request.user.tenant.billing
        subscription = billing.get_subscription()

        if not subscription:
            # No subscription setup yet, so just return a 400.
            return Response(status=status.HTTP_400_BAD_REQUEST)

        result = chargebee.Subscription.cancel(subscription.id, {'end_of_term': True})

        subscription_status = result.subscription.status

        success = (subscription_status == 'cancelled' or subscription_status == 'non_renewing')

        if success:
            billing.cancels_on = datetime.fromtimestamp(result.subscription.current_term_end)
            billing.save()

        return Response({'success': success}, content_type='application/json')

    @list_route(methods=['GET'])
    def start_trial(self, request):
        success = False
        billing = self.request.user.tenant.billing
        subscription = billing.get_subscription()

        if not subscription or billing.trial_started:
            # No subscription setup yet, so just return a 400.
            return Response(status=status.HTTP_400_BAD_REQUEST)

        plan_id = settings.CHARGEBEE_PRO_TRIAL_PLAN_NAME
        trial_end = datetime.now() + timedelta(days=30)
        # Chargebee wants the time in seconds.
        trial_end = calendar.timegm(trial_end.timetuple())

        result = chargebee.Subscription.update(subscription.id, {
            'plan_id': plan_id,
            'trial_end': trial_end,
        })

        if result.subscription.status == 'in_trial':
            success = True

            billing.trial_started = True
            billing.plan = Plan.objects.get(name=plan_id)
            billing.save()

        return Response({'success': success}, content_type='application/json')
