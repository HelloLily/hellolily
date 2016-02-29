from django.contrib import admin

from .models.models import PhoneNumber, Address, EmailAddress


admin.site.register(PhoneNumber)
admin.site.register(Address)
admin.site.register(EmailAddress)
