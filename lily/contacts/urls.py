from django.conf.urls import patterns, url

from lily.contacts.views import (JsonContactListView, AddContactView, EditContactView, DetailContactView,
                                 DeleteContactView, ListContactView, ExportContactView)


urlpatterns = patterns('',
    url(r'^add/$', AddContactView.as_view(), name='contact_add'),
    url(r'^add/from_account/(?P<account_pk>[\w-]+)/$', AddContactView.as_view(), name='contact_add'),
    url(r'^edit/(?P<pk>[\w-]+)/$', EditContactView.as_view(), name='contact_edit'),
    url(r'^details/(?P<pk>[\w-]+)/$', DetailContactView.as_view(), name='contact_details'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteContactView.as_view(), name='contact_delete'),
    url(r'^json_list/$', JsonContactListView.as_view(), name='json_contact_list'),
    url(r'^export/$', ExportContactView.as_view(), name='contact_export'),
    url(r'^tag/(?P<tag>[\w-]+)/$', ListContactView.as_view(), name='contact_list_filtered_by_tag'),
    url(r'^(?P<b36_pks>[\w;]*)/$', ListContactView.as_view(), name='contact_list_filtered'),
    url(r'^$', ListContactView.as_view(), name='contact_list'),
)
