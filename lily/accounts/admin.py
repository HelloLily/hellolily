from django.contrib import admin

from .models import Account, Website, AccountStatus

admin.site.register(Account)
admin.site.register(Website)
admin.site.register(AccountStatus)
