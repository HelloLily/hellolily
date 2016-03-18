from django.conf.urls import patterns, url

from .views import CreateDealView, DeleteDealView, UpdateDealView

urlpatterns = patterns(
    '',
    url(r'^create/$', CreateDealView.as_view(), name='deal_create'),
    url(r'^create/from_account/(?P<account_pk>[\w-]+)/$', CreateDealView.as_view(), name='deal_create'),
    url(r'^update/(?P<pk>[\w-]+)/$', UpdateDealView.as_view(), name='deal_update'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteDealView.as_view(), name='deal_delete'),
)
