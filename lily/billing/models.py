from django.db import models


class Billing(models.Model):
    subscription_id = models.CharField(max_length=255, blank=True)
    customer_id = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.customer_id + ': ' + self.subscription_id
