from django.contrib import admin
from lily.utils.models import PhoneNumberModel, SocialMediaModel, SocialMediaModel, AddressModel, \
                                EmailAddressModel, NoteModel

admin.site.register(PhoneNumberModel)
admin.site.register(SocialMediaModel)
admin.site.register(AddressModel)
admin.site.register(EmailAddressModel)
admin.site.register(NoteModel)