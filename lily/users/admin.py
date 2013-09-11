from django.contrib import admin

from lily.users.models import CustomUser

admin.site.register(CustomUser)