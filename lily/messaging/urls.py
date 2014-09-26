from django.conf.urls import patterns, url, include
from django.conf import settings

from lily.messaging.views import DashboardView


urlpatterns = patterns('',
    url(r'^$', DashboardView.as_view(), name='messaging_dashboard'),
#     url(r'^sent/$', dashboard_view, name='messaging_sent'),
#     url(r'^drafts/$', dashboard_view, name='messaging_drafts'),
#     url(r'^archived/$', dashboard_view, name='messaging_archived'),
)

for app in settings.MESSAGE_APPS:
    name = app.rpartition('.')[2]
    urlpatterns += patterns('',
        url(r'^%s/' % name, include('%s.urls' % app)),
    )
