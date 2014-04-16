from django.conf.urls import patterns, url

from lily.cases.views import CreateCaseView, DetailCaseView, UpdateCaseView, DeleteCaseView, ListCaseView, \
    UpdateStatusAjaxView, ArchiveCasesView, UnarchiveCasesView, ArchivedCasesView


urlpatterns = patterns(
    '',
    url(r'^create/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^create/from_note/(?P<note_pk>[\w-]+)/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^update/(?P<pk>[\w-]+)/$', UpdateCaseView.as_view(), name='case_update'),
    url(r'^update/status/(?P<pk>[\w-]+)/$', UpdateStatusAjaxView.as_view(), name='case_update_status'),
    url(r'^details/(?P<pk>[\w-]+)/$', DetailCaseView.as_view(), name='case_details'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteCaseView.as_view(), name='case_delete'),
    url(r'^archive_cases/$', ArchiveCasesView.as_view(), name='case_archive'),
    url(r'^unarchive_cases/$', UnarchiveCasesView.as_view(), name='case_unarchive'),
    url(r'^archive/$', ArchivedCasesView.as_view(), name='case_archived_list'),
    url(r'^$', ListCaseView.as_view(), name='case_list'),
)
