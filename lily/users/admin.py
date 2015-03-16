from django.contrib import admin

from .models import LilyUser, LilyGroup


admin.site.register(LilyUser)
admin.site.register(LilyGroup)
