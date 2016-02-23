from django.conf.urls import url, patterns

from .views import SearchView, EmailAddressSearchView


urlpatterns = patterns(
    '',
    url(r'^search/$', SearchView.as_view(), name='search_view'),
    url(r'^emailaddress/(?P<email_address>([-_\.\+\w]+)?@[-_\.\w]+)$',
        EmailAddressSearchView.as_view(),
        name='search_view'),
)
