from django.contrib import admin

from lily.tenant.admin import TenantFilter
from lily.tenant.admin import TenantFilteredChoicesMixin
from .models import LilyUser, Team, UserInfo


@admin.register(LilyUser)
class LilyUserAdmin(TenantFilteredChoicesMixin, admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'full_name',
        'email',
        'is_staff',
        'is_superuser',
        'is_active',
        'tenant',
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        TenantFilter,
    )
    tenant_filtered_fields = (
        'teams',
        'social_media',
    )
    filter_horizontal = (
        'teams',
        'user_permissions',
        'social_media',
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
class TeamAdmin(admin.ModelAdmin):
    list_select_related = ('tenant', )
    list_display = (
        'id',
        'name',
        'tenant',
    )
    search_fields = ('name', )
    list_filter = (TenantFilter, )
