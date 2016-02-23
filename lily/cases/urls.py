from django.conf.urls import patterns, url

from .views import (CreateCaseView, UpdateCaseView, DeleteCaseView, UpdateStatusAjaxView, ArchiveCasesView,
                    UnarchiveCasesView, UpdateAndUnarchiveCaseView, GetCaseTypesView, UpdateAssignedToView)


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
    url(r'^update/assigned_to/(?P<pk>[\w-]+)/$', UpdateAssignedToView.as_view(), name='case_assign_to_user'),
    url(r'^update/assigned_to/$', UpdateAssignedToView.as_view(), name='case_assign_to_user_short'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteCaseView.as_view(), name='case_delete'),
    url(r'^archive/$', ArchiveCasesView.as_view(), name='case_archive'),
    url(r'^unarchive/$', UnarchiveCasesView.as_view(), name='case_unarchive'),
    url(r'^casetypes/$', GetCaseTypesView.as_view(), name='get_casetypes'),
)
