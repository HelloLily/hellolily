from django.conf.urls import url

from .views import SugarCsvImportView, RedirectAccountContactView, DownloadRedirectView

urlpatterns = [
    url(r'^utils/sugarcsvimport/$', SugarCsvImportView.as_view(), name='sugarcsvimport'),
    url(r'^utils/(?P<phone_nr>\+31[0-9]+)/$', RedirectAccountContactView.as_view(), name='sugarcsvimport'),
    url(
        r'^download/(?P<model_name>[A-Za-z]+)/(?P<field_name>[a-z_]+)/(?P<object_id>[0-9]+)/$',
        DownloadRedirectView.as_view(),
        name='download'
    ),
]
