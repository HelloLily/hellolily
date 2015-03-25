from django.conf.urls import patterns, url

from .views import AddContactView, EditContactView, DeleteContactView, ExportContactView


urlpatterns = patterns(
    '',
    url(r'^create/$', AddContactView.as_view(), name='contact_add'),
    url(r'^add/from_account/(?P<account_pk>[\w-]+)/$', AddContactView.as_view(), name='contact_add'),
    url(r'^edit/(?P<pk>[\w-]+)/$', EditContactView.as_view(), name='contact_edit'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteContactView.as_view(), name='contact_delete'),
    url(r'^export/$', ExportContactView.as_view(), name='contact_export'),
)
