from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.static import serve

from lily.utils.views import BaseView, TemplateView

admin.autodiscover()

urlpatterns = [
    url(r'^accounts/', include('lily.accounts.urls')),
    url(r'^cases/', include('lily.cases.urls')),
    url(r'^contacts/', include('lily.contacts.urls')),
    url(r'^deals/', include('lily.deals.urls')),
    url(r'^messaging/email/', include('lily.messaging.email.urls')),
    url(r'^stats/', include('lily.stats.urls')),
    url(r'^', include('lily.users.urls')),
    url(r'^', include('lily.utils.urls')),
    url(r'^taskmonitor/', include('taskmonitor.urls')),
    url(r'^search/', include('lily.search.urls')),
    url(r'^preferences/', include('lily.preferences.urls')),

    # Django admin urls
    url(r'^admin/login/$', RedirectView.as_view(pattern_name='login', permanent=True, query_string=True)),
    url(r'^admin/logout/$', RedirectView.as_view(pattern_name='logout', permanent=True, query_string=True)),
    url(r'^admin/', include(admin.site.urls)),

    # Django rest
    url(r'^api/', include('lily.api.urls')),

    url(r'^$', BaseView.as_view(), name='base_view'),

    url(r'^favicon.ico$', RedirectView.as_view(
        url=settings.STATIC_URL + 'app/images/favicons/favicon.ico',
        permanent=True
    )),
    url(r'^404.html$', TemplateView.as_view(template_name='404.html')),
    url(r'^500.html$', TemplateView.as_view(template_name='500.html')),
]

if settings.DEBUG:
    # Works only in debug mode
    urlpatterns += [
        url(r'^media/(.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        url(r'^static/(.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
