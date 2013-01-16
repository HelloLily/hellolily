from django.conf.urls import patterns, url

from lily.updates.views import delete_blogentry_view


urlpatterns = patterns('',
#     url(r'^add/$', add_blogentry_view, name='blogentry_add'),
     url(r'^delete/(?P<pk>[\w-]+)/$', delete_blogentry_view, name='blogentry_delete'),
)
