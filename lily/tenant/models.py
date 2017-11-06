from django.conf import settings
from django.db import models

from lily.billing.models import Billing
from lily.utils.countries import COUNTRIES
from lily.utils.currencies import CURRENCIES

from .middleware import get_current_user


class TenantManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        """
        Manipulate the returned queryset by adding a filter for tenant using the tenant linked
        to the current logged in user (received via custom middleware).
        """
        user = get_current_user()
        if user and user.is_authenticated():
            return super(TenantManager, self).get_queryset().filter(tenant=user.tenant)
        else:
            return super(TenantManager, self).get_queryset()


class Tenant(models.Model):
    name = models.CharField(max_length=255, blank=True)
    country = models.CharField(blank=True, max_length=2, verbose_name='country', choices=COUNTRIES)
    currency = models.CharField(blank=True, max_length=3, verbose_name='currency', choices=CURRENCIES)
    timelogging_enabled = models.BooleanField(default=False)
    billing = models.ForeignKey(Billing, null=True, blank=True)
    billing_default = models.BooleanField(default=False)

    def __unicode__(self):
        if self.name:
            return self.name

        return unicode("%s %s" % (self._meta.verbose_name.title(), self.pk))


class MultiTenantMixin(models.Model):
    # Automatically filter any queryset by tenant if logged in
    objects = TenantManager()

    # blank=True to allow form validation (tenant is set upon model.save)
    tenant = models.ForeignKey(Tenant, blank=True)

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user and user.is_authenticated() and not self.tenant_id:
            self.tenant = user.tenant

        return super(MultiTenantMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class SingleTenantMixin(models.Model):
    tenant = models.ForeignKey(Tenant, blank=True)

    def save(self, *args, **kwargs):
        self.tenant = Tenant.objects.get_or_create(pk=1)[0]
        return super(SingleTenantMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


TenantMixin = SingleTenantMixin
TenantObjectManager = models.Manager
if settings.MULTI_TENANT:
    TenantMixin = MultiTenantMixin
    TenantObjectManager = TenantManager
