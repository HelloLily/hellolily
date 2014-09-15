from django.contrib import admin

from lily.cases.models import Case, CaseType


admin.site.register(Case)
admin.site.register(CaseType)
