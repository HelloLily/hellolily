from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import TimeLog


@admin.register(TimeLog)
class TimeLogAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', 'user', )
    list_display = (
        'id', 'hours_logged', 'user', 'billable', 'date', 'content', 'gfk_content_type', 'tenant',
    )
    list_display_links = ('id', 'hours_logged', 'user', )
    search_fields = ()
    list_filter = ('billable', 'gfk_content_type', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ('user', )
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'hours_logged',
                'user',
                'billable',
                'date',
                'content',
                'gfk_content_type',
                'gfk_object_id',
            ),
        }),
    )
