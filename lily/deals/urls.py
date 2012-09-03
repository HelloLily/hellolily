from django.conf.urls import patterns, url

from lily.deals.views import detail_deal_view, list_deal_view, add_deal_view, edit_deal_view, \
    edit_stage_view, delete_deal_view


urlpatterns = patterns('',
    url(r'^add/$', add_deal_view, name='deal_add'),
    url(r'^edit/(?P<pk>[\w-]+)/$', edit_deal_view, name='deal_edit'),
    url(r'^edit/stage/(?P<pk>[\w-]+)/$', edit_stage_view, name='deal_edit_stage'),
    url(r'^details/(?P<pk>[\w-]+)/$', detail_deal_view, name='deal_details'),
    url(r'^delete/xhr/(?P<pk>[\w-]+)/$', delete_deal_view, name='deal_delete'),
    url(r'^$', list_deal_view, name='deal_list'),
)