import os

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

from lily.utils.views import BaseView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^accounts/', include('lily.accounts.urls', app_name='accounts')),
    url(r'^contacts/', include('lily.contacts.urls', app_name='contacts')),
    url(r'^cases/', include('lily.cases.urls', app_name='cases')),
    url(r'^deals/', include('lily.deals.urls', app_name='deals')),
    url(r'^notes/', include('lily.notes.urls')),
    url(r'^messaging/', include('lily.messaging.urls')),
    url(r'^provide/', include('lily.provide.urls')),
    url(r'^stats/', include('lily.stats.urls')),
    url(r'^updates/', include('lily.updates.urls')),
    url(r'^', include('lily.users.urls')),
    url(r'^', include('lily.utils.urls')),
    url(r'^taskmonitor/', include('taskmonitor.urls')),
    url(r'^search/', include('lily.search.urls')),
    url(r'^preferences/', include('lily.preferences.urls')),

    # Django admin urls
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Django rest
    url(r'^api/', include('lily.api.urls')),

    url(r'^$', BaseView.as_view(), name='base_view'),

    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    (r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'images/core/favicon.ico')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('', url(r'^__debug__/', include(debug_toolbar.urls)), )

# Works only in debug mode
if os.environ.get('PRODUCTION_MEDIA_URL', None) is None:
    urlpatterns += patterns(
        '',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
