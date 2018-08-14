from django.contrib import admin

from lily.tenant.admin import TenantFilter, TenantFilteredChoicesMixin
from .models import Case, CaseType, CaseStatus


@admin.register(Case)
class CaseAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'subject',
        'description',
        'priority',
        'tenant',
    )
    search_fields = (
        'subject',
        'description',
    )
    list_filter = (
        'priority',
        TenantFilter,
    )
    tenant_filtered_fields = (
        'status',
        'type',
        'assigned_to',
        'assigned_to_teams',
        'created_by',
        'account',
        'contact',
        'parcel',
    )
    filter_horizontal = ('assigned_to_teams', )


@admin.register(CaseType)
class CaseTypeAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'use_as_filter',
        'is_archived',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'use_as_filter',
        'is_archived',
        TenantFilter,
    )


@admin.register(CaseStatus)
class CaseStatusAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'position',
        'name',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'position',
        TenantFilter,
    )
