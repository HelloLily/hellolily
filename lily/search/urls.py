from django.conf.urls import url, patterns

from .views import SearchView


urlpatterns = patterns('',
    url(r'^search/$', SearchView.as_view(), name='search_view'),
)
