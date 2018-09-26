from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models.models import PhoneNumber, Address, EmailAddress, ExternalAppLink


@admin.register(PhoneNumber)
class PhoneNumberAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'number', 'status', 'type', 'other_type', 'tenant', )
    list_display_links = ('id', 'number', )
    search_fields = ('number', )
    list_filter = ('status', 'type', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'number',
                'status',
                'type',
                'other_type',
            ),
        }),
    )


@admin.register(Address)
class AddressAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'full', 'type', 'tenant', )
    list_display_links = ('id', 'full', )
    search_fields = ('address', )
    list_filter = ('state_province', 'type', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'address',
                'postal_code',
                'city',
                'state_province',
                'country',
                'type',
            ),
        }),
    )


@admin.register(EmailAddress)
class EmailAddressAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'email_address', 'status', 'tenant', )
    list_display_links = ('id', 'email_address', )
    search_fields = ('email_address', )
    list_filter = ('status', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'email_address',
                'status',
            ),
        }),
    )


@admin.register(ExternalAppLink)
class ExternalAppLinkAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'url', 'name', 'tenant', )
    list_display_links = ('id', 'url', )
    search_fields = ('url', 'name', )
    list_filter = (TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'url',
                'name',
            ),
        }),
    )
