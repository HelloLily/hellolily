from django.conf.urls import patterns, url

from lily.messaging.email.views import email_inbox_view, email_json_view, edit_email_account_view, \
    list_email_template_view, add_email_template_view, edit_email_template_view, parse_email_template_view, \
    email_html_view, mark_read_view, mark_unread_view, move_trash_view, email_compose_view, email_body_preview_view, \
    email_drafts_view, email_reply_view, email_sent_view, email_trash_view, email_spam_view, \
    email_account_folder_view, email_forward_view, email_configuration_wizard, email_configuration_wizard_template, \
    email_search_view, email_share_wizard, email_proxy_view, email_attachment_removal, email_folder_sync_view, \
    move_messages_view


urlpatterns = patterns('',
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

    # all other urls for account / folder
    url(r'^(?P<account_id>[\d-]+)/(?P<folder>.+)/$', email_account_folder_view, name='messaging_email_account_folder'),

    # hard sync folders
    url(r'^(?P<folder>[^/].+)/(?P<account_id>[\d-]+)/sync$', email_folder_sync_view, name='messaging_email_folder_account_sync'),
    url(r'^(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/sync$', email_folder_sync_view, name='messaging_email_account_folder_sync'),
    url(r'^(?P<folder>[^/].+)/sync$', email_folder_sync_view, name='messaging_email_folder_sync'),

    # compose view
    url(r'^compose/$', email_compose_view, name='messaging_email_compose'),
    url(r'^compose/(?P<pk>[\d-]+)/$', email_compose_view, name='messaging_email_compose'),
    url(r'^compose/(?P<pk>[\d-]+)/remove/attachment/(?P<attachment_pk>[\d-]+)/$', email_attachment_removal, name='email_attachment_removal'),
    url(r'^reply/(?P<pk>[\d-]+)/$', email_reply_view, name='messaging_email_reply'),
    url(r'^forward/(?P<pk>[\d-]+)/$', email_forward_view, name='messaging_email_forward'),
    url(r'^preview/(?P<message_type>[a-z]+)/$', email_body_preview_view, name='messaging_email_body_preview'),
    url(r'^preview/(?P<message_type>[a-z]+)/(?P<object_id>[\d-]+)/$', email_body_preview_view, name='messaging_email_body_preview'),
    url(r'^preview/(?P<message_type>[a-z]+)/(?P<object_id>[\d-]+)/(?P<template_id>[\d-]+)$', email_body_preview_view, name='messaging_email_body_preview'),

    # AJAX views
    url(r'^json/(?P<pk>[\w-]+)/$', email_json_view, name='messaging_email_json'),
    url(r'^html/(?P<pk>[\w-]+)/$', email_html_view, name='messaging_email_html'),
    url(r'^markasread/$', mark_read_view, name='messaging_mark_read'),
    url(r'^markasunread/$', mark_unread_view, name='messaging_mark_unread'),
    url(r'^movetotrash/$', move_trash_view, name='messaging_move_trash'),

    # e-mail account views
    url(r'^account/wizard/share/(?P<pk>[\w-]+)/$', email_share_wizard, name='messaging_email_account_share_template'),
    url(r'^account/wizard/configuration/$', email_configuration_wizard_template, name='messaging_email_account_wizard_template'),
    url(r'^account/wizard/configuration/(?P<pk>[\w-]+)/$', email_configuration_wizard, name='messaging_email_account_wizard'),
    url(r'^account/edit/(?P<pk>[\w-]+)/$', edit_email_account_view, name='messaging_email_account_edit'),
    # url(r'^account/details/(?P<pk>[\w-]+)/$', detail_email_account_view, name='messaging_email_account_details'),

    # e-mail template views
    url(r'^templates/$', list_email_template_view, name='messaging_email_template_list'),
    url(r'^templates/new/$', add_email_template_view, name='messaging_email_template_add'),
    url(r'^templates/edit/(?P<pk>[\d-]+)/$', edit_email_template_view, name='messaging_email_template_edit'),
    url(r'^templates/parse/$', parse_email_template_view, name='messaging_email_template_parse'),

    # other
    url(r'^search/(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/(?P<search_key>.+)/$', email_search_view, name='messaging_email_search'),
    url(r'^search/(?P<folder>[^/].+)/(?P<search_key>[^/].+)/$', email_search_view, name='messaging_email_search_all'),
    url(r'^search/$', email_search_view, name='messaging_email_search_empty'),
    url(r'^attachment/(?P<pk>[\d-]+)/(?P<path>[^/].+)/$', email_proxy_view, name='email_proxy_view'),
    url(r'^movemessages/$', move_messages_view, name='move_messages_view'),
)
