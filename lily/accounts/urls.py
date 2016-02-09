from django.conf.urls import patterns, url

from .views import ExportAccountView


urlpatterns = patterns(
     '',
     url(r'^export/$', ExportAccountView.as_view(), name='account_export'),
)
