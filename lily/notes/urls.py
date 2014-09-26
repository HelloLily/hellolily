from django.conf.urls import patterns, url

from lily.notes.views import DeleteNoteView, UpdateNoteView, UpdateDateNoteView


urlpatterns = patterns(
    '',
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteNoteView.as_view(), name='note_delete'),
    url(r'^update/(?P<pk>[\w-]+)/$', UpdateNoteView.as_view(), name='note_update'),
    url(r'^update_date/(?P<pk>[\w-]+)/$', UpdateDateNoteView.as_view(), name='note_update_date'),
)
