from django.conf.urls import url

from .views import InternalNumberSearchView, PhoneNumberSearchView


urlpatterns = [
    url(r'^number/(?P<number>(\+)?([\d\-]+))$',
        PhoneNumberSearchView.as_view(),
        name='search_view'),
    url(r'^internal-number/(?P<number>(\+)?([\d\-]+))$',
        InternalNumberSearchView.as_view(),
        name='search_view'),
]
