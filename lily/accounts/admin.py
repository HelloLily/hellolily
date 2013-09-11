from django.contrib import admin

from lily.accounts.models import Account, Website

admin.site.register(Account)
admin.site.register(Website)