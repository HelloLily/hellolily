from django.conf.urls import patterns, url

from .views import create_note_view, delete_note_view, edit_note_view, edit_date_note_view


urlpatterns = patterns(
    '',
    url(r'^create/$', create_note_view, name='note_create'),
    url(r'^delete/(?P<pk>[\w-]+)/$', delete_note_view, name='note_delete'),
    url(r'^update/(?P<pk>[\w-]+)/$', edit_note_view, name='note_update'),
    url(r'^update_date/(?P<pk>[\w-]+)/$', edit_date_note_view, name='note_update_date'),
)
