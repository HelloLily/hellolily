from django.conf.urls import patterns, url

from lily.messages.email.views import email_inbox_view, detail_email_sent_view, \
 detail_email_draft_view, detail_email_archive_view, detail_email_compose_view, \
 email_json_view, add_email_account_view, edit_email_account_view, \
 detail_email_account_view, add_email_template_view, edit_email_template_view, \
 detail_email_template_view, parse_email_template_view, email_html_view, \
 mark_read_view, mark_unread_view, move_trash_view


urlpatterns = patterns('',
    # E-mail views
    url(r'^$', email_inbox_view, name='messages_email_inbox'),
    url(r'^sent/$', detail_email_sent_view, name='messages_email_sent'),
    url(r'^drafts/$', detail_email_draft_view, name='messages_email_drafts'),
    url(r'^archived/$', detail_email_archive_view, name='messages_email_archived'),
    url(r'^trash/$', detail_email_archive_view, name='messages_email_trash'),
    url(r'^compose/$', detail_email_compose_view, name='messages_email_compose'),
    url(r'^nextsteps/$', detail_email_compose_view, name='messages_email_next_steps'),

    url(r'^json/(?P<pk>[\w-]+)/$', email_json_view, name='messages_email_json'),
    url(r'^html/(?P<pk>[\w-]+)/$', email_html_view, name='messages_email_html'),

    # AJAX views
    url(r'^markasread/$', mark_read_view, name='messages_mark_read'),
    url(r'^markasunread/$', mark_unread_view, name='messages_mark_unread'),
    url(r'^movetotrash/$', move_trash_view, name='messages_move_trash'),

    # E-mail account views
    url(r'^account/add/$', add_email_account_view, name='messages_email_account_add'),
    url(r'^account/edit/(?P<pk>[\w-]+)/$', edit_email_account_view, name='messages_email_account_edit'),
    url(r'^account/details/(?P<pk>[\w-]+)/$', detail_email_account_view, name='messages_email_account_details'),

    # E-mail template views
    url(r'^template/new/$', add_email_template_view, name='messages_email_template_add'),
    url(r'^template/edit/(?P<pk>[\d-]+)/$', edit_email_template_view, name='messages_email_template_edit'),
    url(r'^template/details/(?P<pk>[\w-]+)/$', detail_email_template_view, name='messages_email_template_details'),
    url(r'^template/parse/$', parse_email_template_view, name='messages_email_template_parse'),

)
