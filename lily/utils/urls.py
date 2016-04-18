from django.conf.urls import patterns, url

from .views import ajax_update_view, notifications_view
from .views import SugarCsvImportView, RedirectAccountContactView, DownloadRedirectView

urlpatterns = patterns(
    '',
    url(r'^ajax/(?P<app_name>[A-Za-z]+)/(?P<model_name>[A-Za-z]+)/(?P<object_id>[0-9]+)/$',
        ajax_update_view, name='ajax_update_view'),
    url(r'^utils/notifications.js$', notifications_view, name='notifications'),
    url(r'^utils/sugarcsvimport/$', SugarCsvImportView.as_view(), name='sugarcsvimport'),
    url(r'^utils/(?P<phone_nr>\+31[0-9]+)/$', RedirectAccountContactView.as_view(), name='sugarcsvimport'),
    url(r'^download/(?P<model_name>[A-Za-z]+)/(?P<field_name>[a-z_]+)/(?P<object_id>[0-9]+)/$',
        DownloadRedirectView.as_view(), name='download'),
)
