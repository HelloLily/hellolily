from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import Deal, DealNextStep, DealWhyCustomer, DealWhyLost, DealFoundThrough, DealContactedBy, DealStatus


@admin.register(Deal)
class DealAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', 'status', )
    list_display = ('id', 'name', 'currency', 'amount_once', 'amount_recurring', 'status', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', )
    list_filter = ('currency', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = (
        'assigned_to', 'created_by', 'next_step', 'why_customer', 'why_lost', 'account', 'contact', 'found_through',
        'contacted_by',
    )
    filter_horizontal = ('assigned_to_teams', )
    readonly_fields = ('tenant', 'created', 'modified', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'account',
                'contact',
                'created_by',
                'assigned_to',
                'description',
                'status',
                'found_through',
                'contacted_by',
                'next_step',
                'why_customer',
                'why_lost',
                'newly_assigned',
                'currency',
                'amount_once',
                'amount_recurring',
                'closed_date',
                'quote_id',
                'next_step_date',
                'import_id',
                'imported_from',
                'new_business',
                'is_checked',
                'twitter_checked',
                'card_sent',
                'created',
                'modified',
                'deleted',
                'is_deleted',
                'is_archived',
                'assigned_to_teams',
            ),
        }),
    )


@admin.register(DealNextStep)
class DealNextStepAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'name', 'date_increment', 'position', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', )
    list_filter = ('date_increment', 'position', TenantFilter, )

    # Form view settings.
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'date_increment',
                'position',
            ),
        }),
    )


@admin.register(DealWhyCustomer)
class DealWhyCustomerAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
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
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'position',
            ),
        }),
    )


@admin.register(DealWhyLost)
class DealWhyLostAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
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
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'position',
            ),
        }),
    )


@admin.register(DealFoundThrough)
class DealFoundThroughAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
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
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'position',
            ),
        }),
    )


@admin.register(DealContactedBy)
class DealContactedByAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
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
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'position',
            ),
        }),
    )


@admin.register(DealStatus)
class DealStatusAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
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
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'position',
            ),
        }),
    )
