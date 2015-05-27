from django.conf.urls import patterns, url

from .views import AddAccountView, EditAccountView, ExportAccountView


urlpatterns = patterns('',
     url(r'^create/$', AddAccountView.as_view(), name='account_add'),
     url(r'^(?P<pk>[\w-]+)/edit/$', EditAccountView.as_view(), name='account_edit'),
     url(r'^export/$', ExportAccountView.as_view(), name='account_export'),
)
