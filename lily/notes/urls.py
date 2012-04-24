from django.conf.urls import patterns, url

from lily.notes.views import delete_note_view

urlpatterns = patterns('',
     url(r'^delete/(?P<pk>[\w-]+)/$', delete_note_view, name='note_delete'),
)