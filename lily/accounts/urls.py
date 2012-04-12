from django.conf.urls import patterns, url
from lily.accounts.views import AddAccountView, EditAccountView, DeleteAccountView, ListAccountView

urlpatterns = patterns('',
     url(r'^add/?xhr$', AddAccountView.as_view(), name='account_add_xhr'),
     url(r'^add/$', AddAccountView.as_view(), name='account_add'),
     url(r'^edit/(?P<pk>[\w-]+)/$', EditAccountView.as_view(), name='account_edit'),
     url(r'^delete/xhr/(?P<pk>[\w-]+)/$', DeleteAccountView.as_view(), name='account_delete'),
     url(r'^$', ListAccountView.as_view(), name='account_list'),
)
