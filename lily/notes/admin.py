from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import Note


@admin.register(Note)
class NoteAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', 'author', )
    list_display = (
        'id', 'author', 'is_pinned', 'tenant',
    )
    list_display_links = ('id', 'author', )
    search_fields = ()
    list_filter = ('is_pinned', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ('author', )
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'author',
                'is_pinned',
                'content',
                'gfk_content_type',
                'gfk_object_id',
            ),
        }),
    )
