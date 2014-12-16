from django.conf.urls import patterns, url

from lily.cases.views import CreateCaseView, DetailCaseView, UpdateCaseView, DeleteCaseView, ListCaseView, \
    UpdateStatusAjaxView, ArchiveCasesView, UnarchiveCasesView, UpdateAndUnarchiveCaseView


urlpatterns = patterns(
    '',
    url(r'^create/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^create/from_note/(?P<note_pk>[\w-]+)/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^create/from_contact/(?P<contact_pk>[\w-]+)/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^create/from_account/(?P<account_pk>[\w-]+)/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^update/(?P<pk>[\w-]+)/$', UpdateCaseView.as_view(), name='case_update'),
    url(r'^update/unarchive/(?P<pk>[\w-]+)/$', UpdateAndUnarchiveCaseView.as_view(), name='case_update_unarchive'),
    url(r'^update/status/(?P<pk>[\w-]+)/$', UpdateStatusAjaxView.as_view(), name='case_update_status'),
    url(r'^update/status/$', UpdateStatusAjaxView.as_view(), name='case_update_status_short'),
    url(r'^details/(?P<pk>[\w-]+)/$', DetailCaseView.as_view(), name='case_details'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteCaseView.as_view(), name='case_delete'),
    url(r'^archive/$', ArchiveCasesView.as_view(), name='case_archive'),
    url(r'^unarchive/$', UnarchiveCasesView.as_view(), name='case_unarchive'),
    url(r'^$', ListCaseView.as_view(), name='case_list'),
)
