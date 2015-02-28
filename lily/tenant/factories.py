from factory.django import DjangoModelFactory

from .models import Tenant


class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant
