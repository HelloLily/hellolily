from datetime import datetime
from errno import ETIMEDOUT

import chargebee
from django.conf import settings
from django.db import models
from django.utils.timezone import utc


class BillingInvoice(models.Model):
    invoice_id = models.PositiveIntegerField()


class Plan(models.Model):
    name = models.CharField(max_length=255, unique=True)
    tier = models.PositiveSmallIntegerField(default=0)


class Billing(models.Model):
    subscription_id = models.CharField(max_length=255, blank=True)
    customer_id = models.CharField(max_length=255, blank=True)
    plan = models.ForeignKey(Plan, blank=True, null=True)
    cancels_on = models.DateTimeField(blank=True, null=True)
    free_forever = models.BooleanField(default=False)
    trial_end = models.DateTimeField(blank=True, null=True)

    @property
    def is_free_plan(self):
        if settings.BILLING_ENABLED and not self.free_forever:
            return self.plan.tier == 0
        else:
            # Billing isn't enabled so just return false.
            return False

    @property
    def trial_remaining(self):
        days = 0

        if self.trial_end:
            time_diff = self.trial_end - datetime.now().replace(tzinfo=utc)

            days = time_diff.days

        return days

    def get_customer(self):
        customer = None

        if self.customer_id:
            customer = chargebee.Customer.retrieve(self.customer_id).customer

        return customer

    def get_subscription(self):
        subscription = None

        if self.subscription_id:
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    subscription = chargebee.Subscription.retrieve(self.subscription_id).subscription
                except ETIMEDOUT:
                    # If this is the last attempt, reraise the exception (attempt is zero indexed).
                    if attempt == max_attempts - 1:
                        raise
                else:
                    break

        return subscription

    def get_card(self):
        card = None

        if self.subscription_id:
            card = chargebee.Subscription.retrieve(self.subscription_id).card

        return card

    def update_subscription(self, increment):
        subscription = self.get_subscription()

        if subscription and subscription.plan_id != settings.CHARGEBEE_FREE_PLAN_NAME and not self.free_forever:
            amount = subscription.plan_quantity + increment

            if amount >= 1:
                # Update the amount of users for the subscription.
                chargebee.Subscription.update(subscription.id, {
                    'plan_quantity': amount,
                    'prorate': True,
                    'invoice_immediately': False,
                })

            return True

        return False

    def __unicode__(self):
        return self.customer_id + ': ' + self.subscription_id
