from django.contrib import admin

from lily.tenant.admin import TenantFilter, EstimateCountPaginator
from lily.tenant.admin import TenantFilteredChoicesMixin
from .models import LilyUser, Team, UserInfo, UserInvite


@admin.register(LilyUser)
class LilyUserAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'full_name', 'email', 'is_staff', 'is_superuser', 'is_active', 'tenant', )
    list_display_links = ('id', 'full_name', 'email', )
    search_fields = ('first_name', 'last_name', 'email', )
    list_filter = ('is_staff', 'is_superuser', 'is_active', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ('primary_email_account', 'teams', )
    filter_horizontal = ('groups', 'user_permissions', 'teams', )
    readonly_fields = ('tenant', )
    raw_id_fields = ('info',)
    fieldsets = (
        (None, {
            'fields': (
                'tenant', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'first_name', 'last_name',
                'last_login', 'date_joined', 'picture', 'position', 'phone_number', 'internal_number',
                'language', 'timezone', 'primary_email_account', 'info',
            )
        }),
        ('Related fields', {
            'classes': ('collapse',),
            'fields': (
                'groups',
                'user_permissions',
                'teams',
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Override saving LilyUser model in Django Admin to use password encryption.
        """

        if change:
            # Updating existing user.
            orig_obj = LilyUser.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            # Creating new user.
            obj.set_password(obj.password)
            # Create default onboarding info.
            obj.info = UserInfo.objects.create()

        obj.save()


@admin.register(Team)
class TeamAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'name', 'tenant', )
    list_display_links = ('id', 'name', )
    search_fields = ('name', )
    list_filter = (TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', 'active_users', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'name',
                'active_users',
            ),
        }),
    )


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ()
    list_display = ('id', 'registration_finished', 'email_account_status', )
    list_display_links = ('id', 'registration_finished', )
    search_fields = ()
    list_filter = ('registration_finished', )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ()
    fieldsets = (
        (None, {
            'fields': (
                'registration_finished',
                'email_account_status',
            ),
        }),
    )


@admin.register(UserInvite)
class UserInviteAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    # List view settings.
    list_max_show_all = 100
    list_per_page = 50
    ordering = ['-id', ]
    show_full_result_count = False
    paginator = EstimateCountPaginator
    list_select_related = ('tenant', )
    list_display = ('id', 'first_name', 'email', 'date', 'tenant', )
    list_display_links = ('id', 'first_name', )
    search_fields = ('first_name', 'email', )
    list_filter = ('date', TenantFilter, )

    # Form view settings.
    tenant_filtered_fields = ()
    filter_horizontal = ()
    readonly_fields = ('tenant', 'date', )
    fieldsets = (
        (None, {
            'fields': (
                'tenant',
                'first_name',
                'email',
                'date',
            ),
        }),
    )
