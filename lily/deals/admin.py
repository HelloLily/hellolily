from django.contrib import admin

from .models import Deal, DealNextStep, DealWhyCustomer

admin.site.register(Deal)
admin.site.register(DealNextStep)
admin.site.register(DealWhyCustomer)
