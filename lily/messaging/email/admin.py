from django.contrib import admin

from .models.models import EmailAccount, EmailMessage, EmailTemplate

admin.site.register(EmailAccount)
admin.site.register(EmailMessage)
admin.site.register(EmailTemplate)
