from django.conf.urls import patterns, url

from lily.accounts.views import add_account_view, edit_account_view, delete_account_view, \
    list_account_view, detail_account_view


urlpatterns = patterns('',
     url(r'^add/\?xhr$', add_account_view, name='account_add_xhr'),
     url(r'^add/$', add_account_view, name='account_add'),
     url(r'^edit/(?P<pk>[\w-]+)/$', edit_account_view, name='account_edit'),
     url(r'^details/(?P<pk>[\w-]+)/$', detail_account_view, name='account_details'),
     url(r'^delete/xhr/(?P<pk>[\w-]+)/$', delete_account_view, name='account_delete'),
     url(r'^$', list_account_view, name='account_list'),
)
