from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'^accounts/', include('lily.accounts.urls')),
    url(r'^contacts/', include('lily.contacts.urls')),
    url(r'^', include('lily.users.urls')),
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog', name='jsi18n'),
)

if settings.DEBUG:
    from django.contrib import admin
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    admin.autodiscover()
    
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    urlpatterns += staticfiles_urlpatterns()