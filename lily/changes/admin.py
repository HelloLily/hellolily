from django.contrib import admin

from lily.changes.models import Change
from lily.tenant.admin import TenantFilter, TenantFilteredChoicesMixin, EstimateCountPaginator


@admin.register(Change)
class ChangeAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant',)
    list_display = ('id', 'action', 'tenant',)
    list_display_links = ('id', 'action',)
    search_fields = ('action',)
    list_filter = (TenantFilter, 'action', 'content_type')

    # Form view settings.
    readonly_fields = ('tenant', 'created', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'action',
                'data',
                'user',
                'content_type',
                'object_id',
                'created',
            ),
        }),
    )
