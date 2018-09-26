from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import Tag


@admin.register(Tag)
class TagAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', 'content_type', )
    list_display = ('id', 'name', 'content_type', 'object_id', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', )
    list_filter = ('content_type', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'content_type',
                'object_id',
            ),
        }),
    )
