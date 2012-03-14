from django.conf.urls import patterns, include, url
from django.conf import settings
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
    url(r'^accounts/', include('lily.accounts.urls')),
    url(r'^', include('lily.users.urls')),
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