from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter
from .models import Deal, DealNextStep, DealWhyCustomer, DealWhyLost, DealFoundThrough, DealContactedBy, DealStatus


@admin.register(Deal)
class DealAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'description',
        'currency',
        'amount_once',
        'amount_recurring',
        'status',
        'tenant',
    )
    search_fields = (
        'name',
        'description',
    )
    list_filter = (
        'currency',
        TenantFilter,
    )
    tenant_filtered_fields = (
        'assigned_to',
        'created_by',
        'next_step',
        'why_customer',
        'why_lost',
        'account',
        'contact',
        'found_through',
        'contacted_by',
    )

    def has_add_permission(self, request):
        return False


@admin.register(DealNextStep)
class DealNextStepAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'date_increment',
        'position',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'date_increment',
        'position',
        TenantFilter,
    )


@admin.register(DealWhyCustomer)
class DealWhyCustomerAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'position',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'position',
        TenantFilter,
    )


@admin.register(DealWhyLost)
class DealWhyLostAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'position',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'position',
        TenantFilter,
    )


@admin.register(DealFoundThrough)
class DealFoundThroughAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'position',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'position',
        TenantFilter,
    )


@admin.register(DealContactedBy)
class DealContactedByAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'position',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'position',
        TenantFilter,
    )


@admin.register(DealStatus)
class DealStatusAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'position',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (
        'position',
        TenantFilter,
    )
