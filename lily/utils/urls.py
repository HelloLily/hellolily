from django.conf.urls import patterns, url

from lily.utils.views import ajax_update_view


urlpatterns = patterns('',
    # Update models via Ajax
    url(r'^ajax/(?P<app_name>[A-Za-z]+)/(?P<model_name>[A-Za-z]+)/(?P<object_id>[0-9]+)/$', ajax_update_view, name='ajax_update_view'),
)