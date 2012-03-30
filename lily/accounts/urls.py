from django.conf.urls import patterns, url
from lily.accounts.views import AddAccountXHRView, AddAccountView

urlpatterns = patterns('',
     url(r'^add/xhr/$', AddAccountXHRView.as_view(), name='account_add_xhr'),
     url(r'^add/$', AddAccountView.as_view(), name='account_add'),
)
