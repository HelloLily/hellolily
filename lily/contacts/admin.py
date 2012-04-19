from django.contrib import admin
from lily.contacts.models import ContactModel, FunctionModel

admin.site.register(ContactModel)
admin.site.register(FunctionModel)