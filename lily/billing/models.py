import chargebee
from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=255, unique=True)
    tier = models.PositiveSmallIntegerField(default=0)


class Billing(models.Model):
    subscription_id = models.CharField(max_length=255, blank=True, unique=True)
    customer_id = models.CharField(max_length=255, blank=True, unique=True)
    plan = models.ForeignKey(Plan)
    cancels_on = models.DateTimeField(blank=True, null=True)

    @property
    def is_free_plan(self):
        return self.plan.tier == 0

    def get_customer(self):
        customer = None

        if self.customer_id:
            customer = chargebee.Customer.retrieve(self.customer_id).customer

        return customer

    def get_subscription(self):
        subscription = None

        if self.subscription_id:
            subscription = chargebee.Subscription.retrieve(self.subscription_id).subscription

        return subscription

    def get_card(self):
        card = None

        if self.subscription_id:
            card = chargebee.Subscription.retrieve(self.subscription_id).card

        return card

    def update_subscription(self, amount):
        subscription = self.get_subscription()

        if subscription:
            amount = subscription.plan_quantity + amount

            # Update the amount of users for the subscription.
            chargebee.Subscription.update(subscription.id, {
                'plan_quantity': amount,
            })

        return False

    def __unicode__(self):
        return self.customer_id + ': ' + self.subscription_id
