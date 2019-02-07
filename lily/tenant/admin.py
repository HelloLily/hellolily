from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.paginator import Paginator
from django.db import connection

from .models import Tenant


class EstimateCountPaginator(Paginator):
    """
    Overrides the count method to get an estimate instead of actual count when not filtered
    """
    _count = None

    @property
    def count(self):
        """
        Changed to use an estimate if the estimate is greater than 10,000
        Returns the total number of objects, across all pages.
        """
        if self._count is None:
            if self.object_list.query.where:
                self._count = len(self.object_list)
            else:
                estimate = 0
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        'SELECT reltuples FROM pg_class WHERE relname = %s',
                        [self.object_list.query.model._meta.db_table, ]
                    )
                    estimate = int(cursor.fetchone()[0])
                except:
                    pass

                self._count = estimate

        return self._count


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ()
    list_display = ('id', 'name', 'country', 'currency', 'timelogging_enabled', )
    list_display_links = ('id', 'name',)
    search_fields = ('name', )
    list_filter = ('currency', 'timelogging_enabled', 'country', )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'country',
                'currency',
                'billing',
                'timelogging_enabled',
                'billing_default',
            ),
        }),
    )


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
            elif form.base_fields[field_name].required:
                # When creating a new object which has a required field which is related to tenant, allow all possible
                # related models. Since we are the only users of the admin page, we allow the user to add any related
                # field. It could occur that a user adds a field related to tenant A, and tenant B on a different
                # related field. Ideally an additional check should take place for all the fields on an admin form to
                # make sure they are related to the same tenant, if there is any.
                pass
            else:
                # Simply do not allow selecting choices when adding a new obj.
                form.base_fields[field_name].queryset = qs.none()

        return form

    def get_readonly_fields(self, request, obj=None):
        """ When creating a new object, the user should be able to select a tenant. Otherwise, make sure tenant is
        read_only. """
        if not obj:
            return tuple([field for field in self.readonly_fields if field != 'tenant'])
        else:
            return self.readonly_fields


class TenantFilter(SimpleListFilter):
    title = 'tenant'
    parameter_name = 'tenant_id'

    def lookups(self, request, model_admin):
        return [(tenant.id, tenant.name) for tenant in Tenant.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tenant__id__exact=self.value())
        else:
            return queryset
