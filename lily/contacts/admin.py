from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import Contact, Function


@admin.register(Contact)
class ContactAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant',)
    list_display = ('id', 'full_name', 'gender', 'status', 'is_deleted', 'tenant', )
    list_display_links = ('id', 'full_name', )
    search_fields = ('first_name', 'last_name', )
    list_filter = ('gender', 'status', 'is_deleted', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ('phone_numbers', 'social_media', 'addresses', 'email_addresses', )
    filter_horizontal = ('phone_numbers', 'social_media', 'addresses', 'email_addresses', )
    readonly_fields = ('tenant', 'created', 'modified', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'first_name',
                'last_name',
                'description',
                'gender',
                'status',
                'salutation',
                'import_id',
                'created',
                'modified',
                'deleted',
                'is_deleted',
            ),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (
                'phone_numbers',
                'social_media',
                'addresses',
                'email_addresses',
            ),
        }),
    )


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_display = ('id', 'account_id', 'contact_id', )
    list_display_links = ('id', )

    # Form view settings.
    tenant_filtered_fields = ('account', 'contact', 'phone_numbers', 'email_addresses', )
    filter_horizontal = ('phone_numbers', 'email_addresses', )
    readonly_fields = ('created', 'modified', )
    fieldsets = (
        (None, {
            'fields': (
                'account',
                'contact',
                'title',
                'department',
                'is_active',
                'created',
                'modified',
                'is_deleted',
                'deleted',
                'phone_numbers',
                'email_addresses',
            ),
        }),
    )
