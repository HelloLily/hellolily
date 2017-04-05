import chargebee
from django.conf import settings


chargebee.configure(settings.CHARGEBEE_API_KEY, settings.CHARGEBEE_SITE)


def get_customer(tenant):
    billing = tenant.billing
    customer = None

    if billing:
        customer = chargebee.Customer.retrieve(billing.customer_id).customer

    return customer


def get_subscription(tenant):
    billing = tenant.billing
    subscription = None

    if billing:
        subscription = chargebee.Subscription.retrieve(billing.subscription_id).subscription

    return subscription


def get_card(tenant):
    billing = tenant.billing
    card = None

    if billing:
        card = chargebee.Subscription.retrieve(billing.subscription_id).card

    return card


def update_subscription(tenant, amount):
    subscription = get_subscription(tenant)

    if subscription:
        amount = subscription.plan_quantity + amount

        # Update the amount of users for the subscription.
        chargebee.Subscription.update(subscription.id, {
            'plan_quantity': amount,
        })
