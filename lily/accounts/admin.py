from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import Account, Website, AccountStatus


@admin.register(Account)
class AccountAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'name', 'is_deleted', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', )
    list_filter = ('is_deleted', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = (
        'assigned_to', 'status',
        'phone_numbers', 'social_media', 'addresses', 'email_addresses',
    )
    filter_horizontal = ('phone_numbers', 'social_media', 'addresses', 'email_addresses', )
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'assigned_to',
                'deleted',
                'is_deleted',
                'customer_id',
                'status',
                'company_size',
                'logo',
                'description',
                'cocnumber',
                'legalentity',
                'bankaccountnumber',
                'iban',
                'bic',
                'import_id',
            ),
        }),
        ('Advanced options', {
            'classes': ('collapse', ),
            'fields': (
                'phone_numbers',
                'social_media',
                'addresses',
                'email_addresses',
            ),
        }),
    )


@admin.register(AccountStatus)
class AccountStatusAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
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
    list_filter = ('position', TenantFilter, )

    # Form view settings.
    readonly_fields = ('tenant',)


@admin.register(Website)
class AccountWebsiteAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'website', 'account', 'is_primary', 'tenant', )
    list_display_links = ('id', 'website', )
    search_fields = ('website', )
    list_filter = ('is_primary', TenantFilter, )

    # Form view settings.
    readonly_fields = ('tenant',)
