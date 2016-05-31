from django.contrib import admin

from .models import SocialMedia


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'username',
        'profile_url',
        'other_name',
    )
