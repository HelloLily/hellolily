from django.conf.urls import patterns, url

from taskmonitor.views import TaskStatusView

urlpatterns = patterns(
    '',
    url(r'^task/status/(?P<task_id>[\w-]+)/$', TaskStatusView.as_view(), name='task_status'),
)
