from django.conf.urls import patterns, url

from lily.deals.views import ArchiveDealsView, ArchivedDealsView, CreateDealView, DetailDealView, DeleteDealView, \
    UpdateDealView, ListDealView, UpdateStageAjaxView, UnarchiveDealsView, UpdateAndUnarchiveDealView

urlpatterns = patterns(
    '',
    url(r'^create/$', CreateDealView.as_view(), name='deal_create'),
    url(r'^update/(?P<pk>[\w-]+)/$', UpdateDealView.as_view(), name='deal_update'),
    url(r'^update/stage/(?P<pk>[\w-]+)/$', UpdateStageAjaxView.as_view(), name='deal_update_stage'),
    url(r'^update/unarchive/(?P<pk>[\w-]+)/$', UpdateAndUnarchiveDealView.as_view(), name='deal_update_unarchive'),
    url(r'^details/(?P<pk>[\w-]+)/$', DetailDealView.as_view(), name='deal_details'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteDealView.as_view(), name='deal_delete'),
    url(r'^archive/$', ArchiveDealsView.as_view(), name='deal_archive'),
    url(r'^unarchive/$', UnarchiveDealsView.as_view(), name='deal_unarchive'),
    url(r'^archived/$', ArchivedDealsView.as_view(), name='deal_archived_list'),
    url(r'^tag/(?P<tag>[\w-]+)/$', ListDealView.as_view(), name='deal_list_filtered_by_tag'),
    url(r'^archived/tag/(?P<tag>[\w-]+)/$', ArchivedDealsView.as_view(), name='deal_archived_list_filtered_by_tag'),
    url(r'^$', ListDealView.as_view(), name='deal_list'),
)
