from django.contrib import admin

from .models import Call, CallRecord, CallParticipant, CallTransfer

admin.site.register(Call)
admin.site.register(CallRecord)
admin.site.register(CallParticipant)
admin.site.register(CallTransfer)
