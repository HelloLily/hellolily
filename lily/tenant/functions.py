from django.db import models

from .middleware import get_current_user
from .models import Tenant


def add_tenant(model, tenant=None):
    if isinstance(model, models.Model):
        user = get_current_user()

        if tenant:
            pass
        elif user and user.is_authenticated():
            tenant = user.tenant
        else:
            tenant = Tenant.objects.create()

        model.tenant = tenant

    return model, tenant
