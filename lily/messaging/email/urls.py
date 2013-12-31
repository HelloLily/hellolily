from django.conf.urls import patterns, url

from lily.messaging.email.views import email_detail_view, email_html_view, \
    email_inbox_view, email_sent_view, email_drafts_view, email_trash_view, \
    email_spam_view, email_account_folder_view, email_create_view, \
    email_reply_view, email_forward_view, \
    email_body_preview_view, mark_read_view, mark_unread_view, \
    move_trash_view, move_messages_view, email_attachment_proxy_view, \
    email_templates_list_view, create_emailtemplate_view, \
    update_emailtemplate_view, parse_emailtemplate_view, email_search_view, \
    email_configuration_wizard, email_share_wizard


urlpatterns = patterns(
    '',
    # separate email message
    url(r'^details/(?P<pk>[\w-]+)/$', email_detail_view, name='messaging_email_detail'),
    url(r'^html/(?P<pk>[\w-]+)/$', email_html_view, name='messaging_email_html'),

    # predefined folders
    url(r'^inbox/$', email_inbox_view, name='messaging_email_inbox'),
    url(r'^inbox/(?P<account_id>[\d-]+)/$', email_inbox_view, name='messaging_email_account_inbox'),
    url(r'^sent/$', email_sent_view, name='messaging_email_sent'),
    url(r'^sent/(?P<account_id>[\d-]+)/$', email_sent_view, name='messaging_email_account_sent'),
    url(r'^drafts/$', email_drafts_view, name='messaging_email_drafts'),
    url(r'^drafts/(?P<account_id>[\d-]+)/$', email_drafts_view, name='messaging_email_account_drafts'),
    url(r'^trash/$', email_trash_view, name='messaging_email_trash'),
    url(r'^trash/(?P<account_id>[\d-]+)/$', email_trash_view, name='messaging_email_account_trash'),
    url(r'^spam/$', email_spam_view, name='messaging_email_spam'),
    url(r'^spam/(?P<account_id>[\d-]+)/$', email_spam_view, name='messaging_email_account_spam'),

    # all other urls for account + folder
    url(r'^(?P<account_id>[\d-]+)/(?P<folder>.+)/$', email_account_folder_view, name='messaging_email_account_folder'),

    # compose views (create draft, reply, forward, preview)
    url(r'^compose/$', email_create_view, name='messaging_email_compose'),
    url(r'^compose/(?P<pk>[\d-]+)/$', email_create_view, name='messaging_email_compose'),
    url(r'^reply/(?P<pk>[\d-]+)/$', email_reply_view, name='messaging_email_reply'),
    url(r'^forward/(?P<pk>[\d-]+)/$', email_forward_view, name='messaging_email_forward'),

    url(r'^preview/(?P<message_type>[a-z]+)/$', email_body_preview_view, name='messaging_email_body_preview'),
    url(r'^preview/(?P<message_type>[a-z]+)/(?P<object_id>[\d-]+)/$', email_body_preview_view, name='messaging_email_body_preview'),

    url(r'^attachment/(?P<pk>[\d-]+)/(?P<path>[^/].+)/$', email_attachment_proxy_view, name='email_attachment_proxy_view'),

    # do something with email messages
    url(r'^markasread/$', mark_read_view, name='messaging_mark_read'),
    url(r'^markasunread/$', mark_unread_view, name='messaging_mark_unread'),
    url(r'^movetotrash/$', move_trash_view, name='messaging_move_trash'),
    url(r'^movemessages/$', move_messages_view, name='move_messages_view'),

    # email templates
    url(r'^templates/$', email_templates_list_view, name='emailtemplate_list'),
    url(r'^templates/new/$', create_emailtemplate_view, name='emailtemplate_create'),
    url(r'^templates/update/(?P<pk>[\d-]+)/$', update_emailtemplate_view, name='emailtemplate_update'),
    url(r'^templates/parse/$', parse_emailtemplate_view, name='messaging_email_template_parse'),

    # search
    url(r'^search/(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/(?P<search_key>.+)/$', email_search_view, name='messaging_email_search'),
    url(r'^search/(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/$', email_search_view, name='messaging_email_search'),
    url(r'^search/(?P<folder>[^/].+)/(?P<search_key>[^/].+)/$', email_search_view, name='messaging_email_search_all'),
    url(r'^search/(?P<folder>[^/].+)/$', email_search_view, name='messaging_email_search_all'),
    url(r'^search/$', parse_emailtemplate_view, name='messaging_email_search_empty'),

    # emailaccount wizards
    url(r'^account/wizard/configuration/(?P<pk>[\w-]+)/$', email_configuration_wizard, name='messaging_email_account_wizard_template'),
    url(r'^account/wizard/share/(?P<pk>[\w-]+)/$', email_share_wizard, name='messaging_email_account_share_template'),

    # AJAX views
    # url(r'^history-list-json/(?P<pk>[\w-]+)/$', history_list_email_json_view, name='messaging_history_list_email_json'),

    # # e-mail account views
    # url(r'^account/wizard/configuration/(?P<pk>[\w-]+)/$', email_configuration_wizard, name='messaging_email_account_wizard'),
    # url(r'^account/edit/(?P<pk>[\w-]+)/$', edit_email_account_view, name='messaging_email_account_edit'),
    # # url(r'^account/details/(?P<pk>[\w-]+)/$', detail_email_account_view, name='messaging_email_account_details'),
)
