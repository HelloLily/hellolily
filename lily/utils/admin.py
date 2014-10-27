from django.contrib import admin

from lily.utils.models import PhoneNumber, Address, EmailAddress
from lily.socialmedia.models import SocialMedia

admin.site.register(PhoneNumber)
admin.site.register(SocialMedia)
admin.site.register(Address)
admin.site.register(EmailAddress)
