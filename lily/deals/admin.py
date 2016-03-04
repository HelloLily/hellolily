from django.contrib import admin

from .models import Deal, DealNextStep, DealWhyCustomer, DealWhyLost, DealFoundThrough

admin.site.register(Deal)
admin.site.register(DealNextStep)
admin.site.register(DealWhyCustomer)
admin.site.register(DealWhyLost)
admin.site.register(DealFoundThrough)
