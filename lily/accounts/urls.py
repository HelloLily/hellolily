from django.conf.urls import patterns, include, url

from lily.accounts.views import IndexView

urlpatterns = patterns('',
     url(r'^$', IndexView.as_view(), name='accounts_index'),
)