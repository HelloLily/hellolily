from django.contrib import admin

from lily.utils.models import PhoneNumber, SocialMedia, Address, EmailAddress

admin.site.register(PhoneNumber)
admin.site.register(SocialMedia)
admin.site.register(Address)
admin.site.register(EmailAddress)