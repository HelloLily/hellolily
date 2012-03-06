from django.conf.urls import patterns, include, url

from lily.accounts.views import *

urlpatterns = patterns('',
     url(r'^$', IndexView.as_view(), name='accounts_index'),     
     url(r'^base/$', BaseView.as_view(), name='base'),
)