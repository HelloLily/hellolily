from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models import CallRecord, CallParticipant, CallTransfer


@admin.register(CallRecord)
class CallRecordAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'caller', 'destination', 'direction', 'status', 'tenant', )
    list_display_links = ('id', 'caller', 'destination', )
    search_fields = ('caller', 'destination', )
    list_filter = ('direction', 'status', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ('caller', 'destination', )
    readonly_fields = ('tenant', 'call_id', 'direction', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'call_id',
                'direction',
                'caller',
                'destination',
                'status',
                'start',
                'end',
            ),
        }),
    )


@admin.register(CallParticipant)
class CallParticipantAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'name', 'number', 'internal_number', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', 'number', 'internal_number', )
    list_filter = (TenantFilter, )

    # Form view settings.
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'number',
                'internal_number',
            ),
        }),
    )


@admin.register(CallTransfer)
class CallTransferAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'timestamp', 'call', 'destination', 'tenant', )
    list_display_links = ('id', 'timestamp', )
    search_fields = ('destination', )
    list_filter = (TenantFilter, )

    # Form view settings.
    readonly_fields = ('tenant', 'call', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'timestamp',
                'call',
                'destination',
            ),
        }),
    )
