from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/', include('lily.accounts.urls')),
    url(r'^contacts/', include('lily.contacts.urls')),
    url(r'^notes/', include('lily.notes.urls')),
    url(r'^', include('lily.users.urls')),
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog', name='jsi18n'),
    
    # Django admin urls
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Static files and media
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)