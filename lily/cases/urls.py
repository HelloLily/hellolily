from django.conf.urls import patterns, url

from lily.cases.views import CreateCaseView, DetailCaseView, UpdateCaseView, DeleteCaseView, ListCaseView, \
    delete_case_view, update_status_view, archive_case_view


urlpatterns = patterns(
    '',
    url(r'^create/$', create_case_view, name='case_create'),
    url(r'^create/from_note/(?P<note_pk>[\w-]+)/$', create_case_view, name='case_create'),
    url(r'^update/(?P<pk>[\w-]+)/$', update_case_view, name='case_update'),
    url(r'^update/status/(?P<pk>[\w-]+)/$', update_status_view, name='case_update_status'),
    url(r'^details/(?P<pk>[\w-]+)/$', detail_case_view, name='case_details'),
    url(r'^delete/(?P<pk>[\w-]+)/$', delete_case_view, name='case_delete'),
    url(r'^archive/(?P<pk>[\w-]+)/$', archive_case_view, name='case_archive'),
    url(r'^$', list_case_view, name='case_list'),
)
