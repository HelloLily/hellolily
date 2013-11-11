from django.conf.urls import patterns, url

from lily.deals.views import detail_deal_view, list_deal_view, create_deal_view, update_deal_view, \
    update_stage_view, delete_deal_view


urlpatterns = patterns('',
    url(r'^create/$', create_deal_view, name='deal_create'),
    url(r'^update/(?P<pk>[\w-]+)/$', update_deal_view, name='deal_update'),
    url(r'^update/stage/(?P<pk>[\w-]+)/$', update_stage_view, name='deal_update_stage'),
    url(r'^details/(?P<pk>[\w-]+)/$', detail_deal_view, name='deal_details'),
    url(r'^delete/(?P<pk>[\w-]+)/$', delete_deal_view, name='deal_delete'),
    url(r'^$', list_deal_view, name='deal_list'),
)