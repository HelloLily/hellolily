from django.db import models

from lily.multitenant.middleware import get_current_user


class MultiTenantManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        """
        Manipulate the returned query set by adding a filter for tenant by using the tenant linked
        to the current logged in user (received via custom middleware).
        """
        return super(MultiTenantManager, self).get_query_set().filter(tenant=get_current_user().tenant)


class TenantModel(models.Model):
    pass


class MultiTenantMixin(models.Model):
    objects = MultiTenantManager()
    tenant = models.ForeignKey(TenantModel)
    
    class Meta:
        abstract = True