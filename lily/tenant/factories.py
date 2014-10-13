from factory.django import DjangoModelFactory

from lily.tenant.models import Tenant


class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant
