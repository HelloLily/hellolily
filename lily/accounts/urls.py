from django.conf.urls import patterns, url

from lily.accounts.views import add_account_view, edit_account_view, delete_account_view, \
    list_account_view, detail_account_view, exist_account_view, JsonAccountListView


urlpatterns = patterns('',
     url(r'^add/$', add_account_view, name='account_add'),
     url(r'^edit/(?P<pk>[\w-]+)/$', edit_account_view, name='account_edit'),
     url(r'^details/(?P<pk>[\w-]+)/$', detail_account_view, name='account_details'),
     url(r'^delete/(?P<pk>[\w-]+)/$', delete_account_view, name='account_delete'),
     url(r'^json_list/$', JsonAccountListView.as_view(), name='json_account_list'),
     url(r'^tag/(?P<tag>[\w-]+)/$', list_account_view, name='account_list_filtered_by_tag'),
     url(r'^(?P<b36_pks>[\w;]*)/$', list_account_view, name='account_list_filtered'),
     url(r'^exists/(?P<account_name>.*)/$', exist_account_view, name='account_exists'),
     url(r'^$', list_account_view, name='account_list'),
)
