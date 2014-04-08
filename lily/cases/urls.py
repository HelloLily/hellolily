from django.conf.urls import patterns, url

from lily.cases.views import CreateCaseView, DetailCaseView, UpdateCaseView, DeleteCaseView, ListCaseView, \
    UpdateStatusAjaxView


urlpatterns = patterns(
    '',
    url(r'^create/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^create/from_note/(?P<note_pk>[\w-]+)/$', CreateCaseView.as_view(), name='case_create'),
    url(r'^update/(?P<pk>[\w-]+)/$', UpdateCaseView.as_view(), name='case_update'),
    url(r'^update/status/(?P<pk>[\w-]+)/$', UpdateStatusAjaxView.as_view(), name='case_update_status'),
    url(r'^details/(?P<pk>[\w-]+)/$', DetailCaseView.as_view(), name='case_details'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteCaseView.as_view(), name='case_delete'),
    url(r'^$', ListCaseView.as_view(), name='case_list'),
)
