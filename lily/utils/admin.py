from django.contrib import admin

from lily.utils.models import PhoneNumber, SocialMedia, Address, EmailAddress, Note, Tag

admin.site.register(PhoneNumber)
admin.site.register(SocialMedia)
admin.site.register(Address)
admin.site.register(EmailAddress)
admin.site.register(Note)
admin.site.register(Tag)