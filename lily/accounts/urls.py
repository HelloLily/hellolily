from django.conf.urls import url

from .views import ExportAccountView

urlpatterns = [
    url(r'^export/$', ExportAccountView.as_view(), name='account_export'),
]
