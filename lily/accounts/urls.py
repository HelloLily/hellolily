from django.conf.urls import patterns, url
from lily.accounts.views import AddAccountXHRView, AddAccountView, EditAccountView, DeleteAccountView

urlpatterns = patterns('',
     url(r'^add/xhr/$', AddAccountXHRView.as_view(), name='account_add_xhr'),
     url(r'^add/$', AddAccountView.as_view(), name='account_add'),
     url(r'^edit/(?P<pk>[\w-]+)/$', EditAccountView.as_view(), name='account_edit'),
     url(r'^delete/xhr/(?P<pk>[\w-]+)/$', DeleteAccountView.as_view(), name='account_delete'),
     url(r'^$', AddAccountView.as_view(), name='account_list'),
)
