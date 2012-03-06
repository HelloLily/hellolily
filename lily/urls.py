from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', include('lily.accounts.urls')),
)

if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()
    
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )
    