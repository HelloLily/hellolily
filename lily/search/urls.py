from django.conf.urls import url

from .views import SearchView, EmailAddressSearchView, PhoneNumberSearchView, WebsiteSearchView


urlpatterns = [
    url(r'^search/$', SearchView.as_view(), name='search_view'),
    url(r'^website/(?P<website>([-_\.\+\w]+((\/[-_\.\+\w]+)+)?))$',
        WebsiteSearchView.as_view(),
        name='search_view'),
    url(r'^emailaddress/(?P<email_address>([-_\.\+\w]+)?@[-_\.\w]+)$',
        EmailAddressSearchView.as_view(),
        name='search_view'),
    url(r'^number/(?P<number>(\+)?([\d\-]+))$',
        PhoneNumberSearchView.as_view(),
        name='search_view'),
]
