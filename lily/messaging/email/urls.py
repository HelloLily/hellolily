from django.conf.urls import patterns, url

from lily.messaging.email.views import email_inbox_view, detail_email_sent_view, \
 detail_email_draft_view, detail_email_archive_view, detail_email_compose_view, \
 email_json_view, add_email_account_view, edit_email_account_view, \
 detail_email_account_view, add_email_template_view, edit_email_template_view, \
 detail_email_template_view, parse_email_template_view, email_html_view, \
 mark_read_view, mark_unread_view, move_trash_view, email_compose_view, \
 email_compose_template_view, email_drafts_view, email_reply_view, email_forward_view


urlpatterns = patterns('',
    # folders/labels
    url(r'^$', email_inbox_view, name='messaging_email_inbox'),
    url(r'^sent/$', detail_email_sent_view, name='messaging_email_sent'),
    url(r'^drafts/$', email_drafts_view, name='messaging_email_drafts'),
    url(r'^archived/$', detail_email_archive_view, name='messaging_email_archived'),
    url(r'^trash/$', detail_email_archive_view, name='messaging_email_trash'),
    url(r'^nextsteps/$', detail_email_compose_view, name='messaging_email_next_steps'),

    # compose view
    url(r'^compose/$', email_compose_view, name='messaging_email_compose'),
    url(r'^compose/(?P<pk>[\d-]+)/$', email_compose_view, name='messaging_email_compose'),
    url(r'^reply/(?P<pk>[\d-]+)/$', email_reply_view, name='messaging_email_reply'),
    url(r'^forward/(?P<pk>[\d-]+)/$', email_forward_view, name='mmessaging_email_forward'),
    url(r'^compose/template/$', email_compose_template_view, name='messaging_email_compose_template'),
    url(r'^compose/template/(?P<pk>[\d-]+)/$', email_compose_template_view, name='messaging_email_compose_template'),

    # AJAX views
    url(r'^json/(?P<pk>[\w-]+)/$', email_json_view, name='messaging_email_json'),
    url(r'^html/(?P<pk>[\w-]+)/$', email_html_view, name='messaging_email_html'),
    url(r'^markasread/$', mark_read_view, name='messaging_mark_read'),
    url(r'^markasunread/$', mark_unread_view, name='messaging_mark_unread'),
    url(r'^movetotrash/$', move_trash_view, name='messaging_move_trash'),

    # e-mail account views
    url(r'^account/add/$', add_email_account_view, name='messaging_email_account_add'),
    url(r'^account/edit/(?P<pk>[\w-]+)/$', edit_email_account_view, name='messaging_email_account_edit'),
    url(r'^account/details/(?P<pk>[\w-]+)/$', detail_email_account_view, name='messaging_email_account_details'),

    # e-mail template views
    url(r'^template/new/$', add_email_template_view, name='messaging_email_template_add'),
    url(r'^template/edit/(?P<pk>[\d-]+)/$', edit_email_template_view, name='messaging_email_template_edit'),
    url(r'^template/details/(?P<pk>[\w-]+)/$', detail_email_template_view, name='messaging_email_template_details'),
    url(r'^template/parse/$', parse_email_template_view, name='messaging_email_template_parse'),

)
