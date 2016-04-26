from django.conf.urls import patterns, url

from .views import ExportContactView


urlpatterns = patterns(
    '',
    url(r'^export/$', ExportContactView.as_view(), name='contact_export'),
)
