from django.contrib import admin

from lily.tenant.admin import TenantFilter, TenantFilteredChoicesMixin
from .models import Case, CaseType, CaseStatus


@admin.register(Case)
class CaseAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    list_select_related = (
        'tenant',
        'status',
        'type',
        'assigned_to',
        'created_by',
        'account',
        'contact',
    )
    list_display = (
        'id',
        'subject',
        'description',
        'priority',
        'status',
        'type',
        'assigned_to',
        'created_by',
        'account',
        'contact',
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
        'assigned_to_groups',
        'created_by',
        'account',
        'contact',
        'parcel',
    )
    filter_horizontal = (
        'assigned_to_groups',
    )


@admin.register(CaseType)
class CaseTypeAdmin(admin.ModelAdmin):
    list_select_related = (
        'tenant',
    )
    list_display = (
        'id',
        'type',
        'use_as_filter',
        'is_archived',
        'tenant',
    )
    search_fields = (
        'type',
    )
    list_filter = (
        'use_as_filter',
        'is_archived',
        TenantFilter,
    )


@admin.register(CaseStatus)
class CaseStatusAdmin(admin.ModelAdmin):
    list_select_related = (
        'tenant',
    )
    list_display = (
        'id',
        'position',
        'status',
        'tenant',
    )
    search_fields = (
        'status',
    )
    list_filter = (
        'position',
        TenantFilter,
    )
