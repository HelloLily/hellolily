from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import SocialMedia


@admin.register(SocialMedia)
class SocialMediaAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'name', 'username', 'profile_url', 'other_name', 'tenant', )
    list_display_links = ('id', 'username', )
    search_fields = ('username', )
    list_filter = ('name', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'username',
                'profile_url',
                'other_name',
            ),
        }),
    )
