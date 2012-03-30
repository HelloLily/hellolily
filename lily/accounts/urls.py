from django.conf.urls import patterns, url
from lily.accounts.views import AddAccountMinimalView, AddAccountView

urlpatterns = patterns('',
     url(r'^add/minimal/$', AddAccountMinimalView.as_view(), name='account_add_minimal'),
     url(r'^add/$', AddAccountView.as_view(), name='account_add'),
)