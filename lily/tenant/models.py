from django.conf import settings
from django.db import models
from django.db.models import Q
from polymorphic import PolymorphicManager, PolymorphicModel
from lily.utils.countries import COUNTRIES

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


class PolymorphicTenantManager(TenantManager, PolymorphicManager):
    pass


class Tenant(models.Model):
    name = models.CharField(max_length=255, blank=True)
    country = models.CharField(blank=True, max_length=2, verbose_name='country', choices=COUNTRIES)

    def __unicode__(self):
        if self.name:
            return self.name

        return unicode("%s %s" % (self._meta.verbose_name.title(), self.pk))


class NullableTenantManager(models.Manager):
    """
    Allows the tenant of a model to be null.
    """
    def get_queryset(self):
        user = get_current_user()
        if user and user.is_authenticated():
            return super(NullableTenantManager, self).get_queryset().filter(Q(tenant=user.tenant) |
                                                                            Q(tenant__isnull=True))
        else:
            return super(NullableTenantManager, self).get_queryset()


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


class PolymorphicMultiTenantMixin(PolymorphicModel, MultiTenantMixin):
    # Automatically filter any queryset by tenant if logged in and downcast to lowest possible class
    objects = PolymorphicTenantManager()

    class Meta:
        abstract = True


class SingleTenantMixin(models.Model):
    tenant = models.ForeignKey(Tenant, blank=True)

    def save(self, *args, **kwargs):
        self.tenant = Tenant.objects.get_or_create(pk=1)[0]
        return super(SingleTenantMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class PolymorphicSingleTenantMixin(PolymorphicModel, SingleTenantMixin):

    class Meta:
        abstract = True


class NullableTenantMixin(models.Model):
    """
    Mixin which can be used to allow the tenant of an object to be null.
    Not inheriting from TenantMixin since tenant needs to be null and fields can't be overwritten.
    """
    objects = NullableTenantManager()
    tenant = models.ForeignKey(Tenant, blank=True, null=True)

    def save(self, *args, **kwargs):
        user = get_current_user()

        # Only set the tenant if it's a new tenant and a user is logged in
        if not self.id and user and user.is_authenticated() and not self.tenant_id:
            self.tenant = user.tenant

        return super(NullableTenantMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


TenantMixin = SingleTenantMixin
PolymorphicTenantMixin = PolymorphicSingleTenantMixin
TenantObjectManager = models.Manager
if settings.MULTI_TENANT:
    TenantMixin = MultiTenantMixin
    PolymorphicTenantMixin = PolymorphicMultiTenantMixin
    TenantObjectManager = TenantManager
