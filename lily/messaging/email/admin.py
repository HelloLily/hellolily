from django.contrib import admin

from lily.tenant.admin import TenantFilteredChoicesMixin, TenantFilter, EstimateCountPaginator
from .models.models import EmailAccount, EmailMessage, EmailTemplate


@admin.register(EmailAccount)
class EmailAccountAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', 'owner', )
    list_display = (
        'id', 'email_address', 'owner', 'privacy', 'is_active', 'is_authorized', 'is_syncing', 'only_new', 'tenant',
    )
    list_display_links = ('id', 'email_address', )
    search_fields = ()
    list_filter = ('privacy', 'is_active', 'is_authorized', 'is_syncing', 'only_new', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ()
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
            ),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (

            ),
        }),
    )


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('account', )
    list_display = (
        'id', 'subject', 'snippet', 'account', 'read', 'has_attachment', 'message_type',
    )
    list_display_links = ('id', 'subject', )
    search_fields = ('subject', 'snippet', )
    list_filter = ('read', 'has_attachment', 'message_type', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = (
        'subject', 'snippet', 'account', 'has_attachment', 'message_type', 'message_id', 'thread_id',
        'received_by', 'received_by_cc', 'sender',
    )
    fieldsets = (
        (None, {
            'fields': (
                'subject',
                'snippet',
                'account',
                'read',
                'has_attachment',
                'message_type',
                'message_type_to_id',
                'body_html',
                'body_text',
                'draft_id',
                'message_id',
                'thread_id',
                'sender',
                'sent_date',
            ),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (
                'labels',
                'received_by',
                'received_by_cc',
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Fitler labels on account_id.
        """
        form = super(EmailMessageAdmin, self).get_form(request, obj, **kwargs)

        qs = form.base_fields['labels'].queryset
        if obj:
            form.base_fields['labels'].queryset = qs.filter(account_id=obj.account_id)
        else:
            # Simply do not allow selecting choices when adding a new obj.
            form.base_fields['labels'].queryset = qs.none()

        return form


@admin.register(EmailTemplate)
class EmailTemplateAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', 'folder', )
    list_display = ('id', 'name', 'subject', 'folder', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', 'subject', )
    list_filter = (TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ('folder', )
    filter_horizontal = ()
    readonly_fields = ('tenant', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'subject',
                'folder',
            ),
        }),
    )
