from django.conf.urls import patterns, url

from .views import add_blogentry_view, delete_blogentry_view


urlpatterns = patterns('',
    url(r'^add/$', add_blogentry_view, name='blogentry_add'),
    url(r'^reply/(?P<pk>[\w-]+)/$', add_blogentry_view, name='blogentry_reply'),
    url(r'^delete/(?P<pk>[\w-]+)/$', delete_blogentry_view, name='blogentry_delete'),
)
