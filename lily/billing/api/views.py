from django.conf import settings

import chargebee
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lily.utils.api.permissions import IsAccountAdmin

from ..functions import get_card, get_customer, get_subscription


class BillingViewSet(ViewSet):
    permission_classes = (IsAccountAdmin, )

    chargebee.configure(settings.CHARGEBEE_API_KEY, settings.CHARGEBEE_SITE)

    @list_route(methods=['GET', 'PATCH'])
    def subscription(self, request):
        customer = get_customer(self.request.user.tenant)
        subscription = get_subscription(self.request.user.tenant)

        if request.method == 'GET':
            card = get_card(self.request.user.tenant)
            plan = chargebee.Plan.retrieve(subscription.plan_id)
            invoices = chargebee.Invoice.list({'customer_id[is]': customer.id})

            data = {
                'customer': customer.values,
                'subscription': subscription.values,
                'card': card.values if card else None,
                'plan': plan.plan.values,
                'invoices': invoices.response,
            }
        elif request.method == 'PATCH':
            parameters = {
                'customer': {
                    'id': customer.id,
                },
                'subscription': {
                    'id': subscription.id,
                    'plan_id': self.request.data.get('plan_id'),
                    'plan_quantity': subscription.plan_quantity
                },
                'embed': False,
            }

            result = chargebee.HostedPage.checkout_existing(parameters)

            data = {
                'url': result.hosted_page.url,
            }

        return Response(data, content_type='application/json')

    @list_route(methods=['GET'])
    def plans(self, request):
        subscription = get_subscription(self.request.user.tenant)
        current_plan = chargebee.Plan.retrieve(subscription.plan_id)
        plans = chargebee.Plan.list({'status[is]': 'active'})

        data = {
            'subscription': subscription.values,
            'current_plan': current_plan.plan.values,
            'plans': plans.response,
        }

        return Response(data, content_type='application/json')

    @list_route(methods=['GET'])
    def update_card(self, request):
        customer = get_customer(self.request.user.tenant)

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
        subscription = get_subscription(self.request.user.tenant)
        result = chargebee.Subscription.cancel(subscription.id)

        success = False

        if result.subscription.status == 'cancelled':
            success = True

        return Response({'success': success}, content_type='application/json')
