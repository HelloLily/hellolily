from django.contrib import admin

from .models import MessagesAccount, Message

admin.site.register(MessagesAccount)
admin.site.register(Message)
