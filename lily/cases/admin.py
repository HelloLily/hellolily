from django.contrib import admin

from lily.tenant.admin import TenantFilter, TenantFilteredChoicesMixin, EstimateCountPaginator
from .models import Case, CaseType, CaseStatus


@admin.register(Case)
class CaseAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'subject', 'priority', 'is_deleted', 'is_archived', 'tenant', )
    list_display_links = ('id', 'subject',)
    search_fields = ('subject',)
    list_filter = ('priority', 'is_deleted', 'is_archived', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = (
        'status', 'type', 'assigned_to', 'assigned_to_teams', 'created_by', 'account', 'contact', 'parcel',
    )
    filter_horizontal = ('assigned_to_teams', )
    readonly_fields = ('tenant',)
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'subject',
                'description',
                'priority',
                'status',
                'type',
                'assigned_to',
                'created_by',
                'account',
                'contact',
                'expires',
                'parcel',
                'billing_checked',
                'newly_assigned',
                'deleted',
                'is_deleted',
                'is_archived',
            ),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (
                'assigned_to_teams',
            ),
        }),
    )


@admin.register(CaseType)
class CaseTypeAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'name', 'use_as_filter', 'is_archived', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', )
    list_filter = ('use_as_filter', 'is_archived', TenantFilter, )

    # Form view settings.
    readonly_fields = ('tenant',)
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'is_archived',
                'name',
                'use_as_filter',
            ),
        }),
    )


@admin.register(CaseStatus)
class CaseStatusAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'name', 'position', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', )
    list_filter = (TenantFilter, 'position', )

    # Form view settings.
    readonly_fields = ('tenant',)
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'position',
                'name',
            ),
        }),
    )
