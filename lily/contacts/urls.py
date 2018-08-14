from django.conf.urls import url

from .views import ExportContactView

urlpatterns = [
    url(r'^export/$', ExportContactView.as_view(), name='contact_export'),
]
