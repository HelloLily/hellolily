from django.conf.urls import patterns, url

from .views import DeleteDealView

urlpatterns = patterns(
    '',
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteDealView.as_view(), name='deal_delete'),
)
