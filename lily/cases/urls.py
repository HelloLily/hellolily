from django.conf.urls import patterns, url

from .views import DeleteCaseView


urlpatterns = patterns(
    '',
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteCaseView.as_view(), name='case_delete'),
)
