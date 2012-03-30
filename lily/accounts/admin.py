from django.contrib import admin
from lily.accounts.models import TagModel, AccountModel

admin.site.register(TagModel)
admin.site.register(AccountModel)