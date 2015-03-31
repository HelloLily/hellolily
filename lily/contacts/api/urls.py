from django.conf.urls import patterns, url

from lily.contacts.api.views import ContactViewSet


urlpatterns = patterns(
    '',
    url(r'^$', ContactViewSet.as_view()),
)
