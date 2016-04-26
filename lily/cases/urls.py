from django.conf.urls import patterns, url

from .views import DeleteCaseView, UpdateStatusAjaxView, UpdateAssignedToView


urlpatterns = patterns(
    '',
    url(r'^update/status/(?P<pk>[\w-]+)/$', UpdateStatusAjaxView.as_view(), name='case_update_status'),
    url(r'^update/status/$', UpdateStatusAjaxView.as_view(), name='case_update_status_short'),
    url(r'^update/assigned_to/(?P<pk>[\w-]+)/$', UpdateAssignedToView.as_view(), name='case_assign_to_user'),
    url(r'^update/assigned_to/$', UpdateAssignedToView.as_view(), name='case_assign_to_user_short'),
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteCaseView.as_view(), name='case_delete'),
)
