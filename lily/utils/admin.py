from django.contrib import admin

from .models.models import PhoneNumber, Address, EmailAddress, ExternalAppLink


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'number',
        'status',
        'type',
        'other_type',
    )


admin.site.register(Address)
admin.site.register(EmailAddress)
admin.site.register(ExternalAppLink)
