from django.conf.urls import patterns, url

from .views import JsonAccountListView, AddAccountView, EditAccountView, DetailAccountView, \
    DeleteAccountView, ListAccountView, ExistsAccountView, ExportAccountView


urlpatterns = patterns('',
     url(r'^create/$', AddAccountView.as_view(), name='account_add'),
     url(r'^(?P<pk>[\w-]+)/edit/$', EditAccountView.as_view(), name='account_edit'),
     url(r'^details/(?P<pk>[\w-]+)/$', DetailAccountView.as_view(), name='account_details'),
     url(r'^delete/(?P<pk>[\w-]+)/$', DeleteAccountView.as_view(), name='account_delete'),
     url(r'^json_list/$', JsonAccountListView.as_view(), name='json_account_list'),
     url(r'^tag/(?P<tag>[\w-]+)/$', ListAccountView.as_view(), name='account_list_filtered_by_tag'),
     url(r'^exists/(?P<account_name>.*)/$', ExistsAccountView.as_view(), name='account_exists'),
     url(r'^export/$', ExportAccountView.as_view(), name='account_export'),
     url(r'^(?P<b36_pks>[\w;]*)/$', ListAccountView.as_view(), name='account_list_filtered'),
     url(r'^$', ListAccountView.as_view(), name='account_list'),
)
