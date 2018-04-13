import freemail
from babel.numbers import get_territory_currencies
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.db import models
from tldextract import tldextract

from lily.billing.models import Billing, Plan
from lily.tenant.utils import create_defaults_for_tenant
from lily.utils.countries import COUNTRIES
from lily.utils.currencies import CURRENCIES

from .middleware import get_current_user


class TenantManager(models.Manager):
    # TODO: use_for_related_fields is deprecated on Django 1.10 and will be removed in Django 2.0.
    use_for_related_fields = True

    def get_queryset(self):
        """
        Manipulate the returned queryset by adding a filter for tenant using the tenant linked
        to the current logged in user (received via custom middleware).
        """
        user = get_current_user()
        if user and user.is_authenticated:
            return super(TenantManager, self).get_queryset().filter(tenant=user.tenant)
        else:
            return super(TenantManager, self).get_queryset()


class Tenant(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True
    )
    # domain = models.CharField(
    #     max_length=255,
    #     null=True,
    #     unique=True  # TODO: do we want this to be unique?
    # )
    country = models.CharField(
        blank=True,
        max_length=2,
        verbose_name='country',
        choices=COUNTRIES
    )
    currency = models.CharField(
        blank=True,
        max_length=3,
        verbose_name='currency',
        choices=CURRENCIES
    )
    billing = models.ForeignKey(
        to=Billing,
        null=True,
        blank=True
    )
    # Defines whether users can log their hours on cases.
    timelogging_enabled = models.BooleanField(
        default=False
    )
    # Defines a default value for the Billable field when a user logs their hours.
    billing_default = models.BooleanField(
        default=False
    )

    @property
    def admin(self):
        admins = self.lilyuser_set.filter(groups__name='account_admin', tenant=self.pk)

        # Prevent the app from breaking if the only account admin is a superuser.
        if admins.filter(is_superuser=False).exists():
            admins = admins.filter(is_superuser=False)

        return admins.first()

    @staticmethod
    def create_tenant(domain='', **extra_fields):
        extra_fields.setdefault('name', '')
        extra_fields.setdefault('country', '')
        extra_fields.setdefault('currency', '')

        if domain and not freemail.is_free(domain):
            # We can guess some field values based on the domain.
            tld = tldextract.extract(domain)
            geo_ip = GeoIP2()

            if not extra_fields['name']:
                # Use the domain of the email address as tenant name.
                extra_fields['name'] = tld.domain.title()

            if not extra_fields['country']:
                country_code = geo_ip.country(tld.registered_domain).get('country_code')
                if country_code in [c[0] for c in COUNTRIES]:
                    extra_fields['country'] = country_code

            if not extra_fields['currency']:
                currency = get_territory_currencies(extra_fields['country'])[-1]
                if currency in [c[0] for c in CURRENCIES]:
                    extra_fields['currency'] = currency

        if settings.BILLING_ENABLED:
            # Chargebee needs extra info on who to bill, so for now only create the plans without activating the trial.
            plan, created = Plan.objects.get_or_create(name=settings.CHARGEBEE_PRO_TRIAL_PLAN_NAME)
            billing = Billing.objects.create(plan=plan)
        else:
            billing = Billing.objects.create()

        tenant = Tenant.objects.create(
            billing=billing,
            **extra_fields
        )

        create_defaults_for_tenant(tenant)

        return tenant

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

        if user and user.is_authenticated and not self.tenant_id:
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
