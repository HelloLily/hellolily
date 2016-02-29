from django.conf.urls import patterns, url

from .views import DataproviderView


urlpatterns = patterns(
    '',
    url(r'^account/(?P<domain>[\.0-9a-zA-Z\-]+)/$', DataproviderView.as_view(), name='provide_account'),
    url(r'^account/$', DataproviderView.as_view(), name='provide_account_short'),
)
