from django.contrib import admin

from lily.messaging.email.models import EmailAccount, EmailMessage

admin.site.register(EmailAccount)
admin.site.register(EmailMessage)
