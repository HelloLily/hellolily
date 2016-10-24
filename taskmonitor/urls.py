from django.conf.urls import url

from taskmonitor.views import TaskStatusView

urlpatterns = [
    url(r'^task/status/(?P<task_id>[\w-]+)/$', TaskStatusView.as_view(), name='task_status'),
]
