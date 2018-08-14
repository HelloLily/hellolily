from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'country',
    )
    search_fields = ('name', )


class TenantFilteredChoicesMixin(object):
    tenant_filtered_fields = ()

    def get_form(self, request, obj=None, **kwargs):
        """
        Do not show all fk, m2m records as choices for this instance.
        """
        object_fields = [field.name for field in self.model._meta.concrete_fields]
        assert 'tenant' in object_fields, '%s has no tenant field' % self.model

        form = super(TenantFilteredChoicesMixin, self).get_form(request, obj, **kwargs)

        for field_name in self.tenant_filtered_fields:
            qs = form.base_fields[field_name].queryset
            if obj:
                form.base_fields[field_name].queryset = qs.filter(tenant=obj.tenant)
            else:
                # Simply do not allow selecting choices when adding a new obj.
                form.base_fields[field_name].queryset = qs.none()
        return form


class TenantFilter(SimpleListFilter):
    title = 'tenant'
    parameter_name = 'tenant_id'

    def lookups(self, request, model_admin):
        tenant_list = set([c.tenant for c in model_admin.model.objects.all()])
        return [(tenant.id, unicode(tenant)) for tenant in tenant_list]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tenant__id__exact=self.value())
        else:
            return queryset
