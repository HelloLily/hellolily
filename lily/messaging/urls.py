from django.conf.urls import patterns, url, include
from django.conf import settings


urlpatterns = patterns('',)

for app in settings.MESSAGE_APPS:
    name = app.rpartition('.')[2]
    urlpatterns += patterns('',
        url(r'^%s/' % name, include('%s.urls' % app, app_name=name)),
    )
