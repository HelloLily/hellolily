from django.contrib import admin

from .models import Case, CaseType, CaseStatus


admin.site.register(Case)
admin.site.register(CaseType)
admin.site.register(CaseStatus)
