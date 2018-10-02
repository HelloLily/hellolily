from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import Parcel


@admin.register(Parcel)
class ParcelAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'provider', 'identifier', 'get_link', 'tenant', )
    list_display_links = ('id', 'provider', )
    search_fields = ('identifier', )
    list_filter = ('provider', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'provider',
                'identifier',
            ),
        }),
    )
