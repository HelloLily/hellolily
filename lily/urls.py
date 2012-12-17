import os

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/', include('lily.accounts.urls')),
    url(r'^contacts/', include('lily.contacts.urls')),
    url(r'^cases/', include('lily.cases.urls')),
    url(r'^deals/', include('lily.deals.urls')),
    url(r'^notes/', include('lily.notes.urls')),
    url(r'^messages/', include('lily.messages.urls')),
    url(r'^provide/', include('lily.provide.urls')),
    url(r'^updates/', include('lily.updates.urls')),
    url(r'^', include('lily.users.urls')),
    url(r'^', include('lily.utils.urls')),
#    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog', name='jsi18n'),
    
    # Django admin urls
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

# Works only in debug mode
if os.environ.get('PRODUCTION_MEDIA_URL', None) is None:
    urlpatterns += patterns('',
       (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
