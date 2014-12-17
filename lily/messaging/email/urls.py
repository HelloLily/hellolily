from django.conf.urls import patterns, url

from lily.messaging.email.views import EmailMessageDetailView, EmailMessageHTMLView, \
    EmailInboxView, EmailSentView, EmailDraftsView, EmailTrashView, EmailSpamView, EmailFolderView, \
    EmailMessageCreateView, EmailMessageReplyView, EmailMessageForwardView, EmailAttachmentProxy, \
    MarkEmailMessageAsReadView, MarkEmailMessageAsUnreadView, TrashEmailMessageView, MoveEmailMessageView, \
    CreateEmailTemplateView, UpdateEmailTemplateView, ParseEmailTemplateView, EmailSearchView, \
    EmailAccountDeleteView, EmailAccountCreateView, EmailAccountUpdateView,\
    EmailAccountListView, EmailAccountShareView, EmailAccountUnsubscribeView, EmailTemplateListView, \
    EmailTemplateDeleteView, EmailTemplateSetDefaultView, EmailTemplateGetDefaultView, DetailEmailTemplateView


urlpatterns = patterns(
    '',
    # separate email message
    url(r'^details/(?P<pk>[\w-]+)/$', EmailMessageDetailView.as_view(), name='messaging_email_detail'),
    url(r'^html/(?P<pk>[\w-]+)/$', EmailMessageHTMLView.as_view(), name='messaging_email_html'),

    # predefined folders
    url(r'^inbox/$', EmailInboxView.as_view(), name='messaging_email_inbox'),
    url(r'^inbox/(?P<account_id>[\d-]+)/$', EmailInboxView.as_view(), name='messaging_email_account_inbox'),
    url(r'^sent/$', EmailSentView.as_view(), name='messaging_email_sent'),
    url(r'^sent/(?P<account_id>[\d-]+)/$', EmailSentView.as_view(), name='messaging_email_account_sent'),
    url(r'^drafts/$', EmailDraftsView.as_view(), name='messaging_email_drafts'),
    url(r'^drafts/(?P<account_id>[\d-]+)/$', EmailDraftsView.as_view(), name='messaging_email_account_drafts'),
    url(r'^trash/$', EmailTrashView.as_view(), name='messaging_email_trash'),
    url(r'^trash/(?P<account_id>[\d-]+)/$', EmailTrashView.as_view(), name='messaging_email_account_trash'),
    url(r'^spam/$', EmailSpamView.as_view(), name='messaging_email_spam'),
    url(r'^spam/(?P<account_id>[\d-]+)/$', EmailSpamView.as_view(), name='messaging_email_account_spam'),

    # all other urls for account + folder
    url(r'^(?P<account_id>[\d-]+)/(?P<folder>.+)/$', EmailFolderView.as_view(), name='messaging_email_account_folder'),

    # compose views (create draft, reply, forward, preview)
    url(r'^compose/$', EmailMessageCreateView.as_view(), name='messaging_email_compose'),
    url(r'^compose/(?P<pk>[\d-]+)/$', EmailMessageCreateView.as_view(), name='messaging_email_compose'),
    url(r'^reply/(?P<pk>[\d-]+)/$', EmailMessageReplyView.as_view(), name='messaging_email_reply'),
    url(r'^forward/(?P<pk>[\d-]+)/$', EmailMessageForwardView.as_view(), name='messaging_email_forward'),

    url(r'^attachment/(?P<pk>[\d-]+)/$', EmailAttachmentProxy.as_view(), name='email_attachment_proxy_view'),

    # do something with email messages
    url(r'^markasread/$', MarkEmailMessageAsReadView.as_view(), name='messaging_mark_read'),
    url(r'^markasunread/$', MarkEmailMessageAsUnreadView.as_view(), name='messaging_mark_unread'),
    url(r'^movetotrash/$', TrashEmailMessageView.as_view(), name='messaging_move_trash'),
    url(r'^movemessages/$', MoveEmailMessageView.as_view(), name='move_messages_view'),

    # email templates
    url(r'^templates/$', EmailTemplateListView.as_view(), name='messaging_email_template_list'),
    url(r'^templates/create/$', CreateEmailTemplateView.as_view(), name='messaging_email_template_create'),
    url(r'^templates/update/(?P<pk>[\d-]+)/$', UpdateEmailTemplateView.as_view(), name='messaging_email_template_update'),
    url(r'^templates/delete/(?P<pk>[\d-]+)/$', EmailTemplateDeleteView.as_view(), name='messaging_email_template_delete'),
    url(r'^templates/parse/$', ParseEmailTemplateView.as_view(), name='messaging_email_template_parse'),
    url(r'^templates/set-default/(?P<pk>[\d-]+)/$', EmailTemplateSetDefaultView.as_view(), name='messaging_email_template_set_default'),
    url(r'^templates/get-default/(?P<account_id>[\d-]+)/$', EmailTemplateGetDefaultView.as_view(), name='messaging_email_template_get_default'),
    url(r'^templates/get-default/$', EmailTemplateGetDefaultView.as_view(), name='messaging_email_template_get_default'),
    url(r'^templates/detail/(?P<template_id>[\d-]+)/$', DetailEmailTemplateView.as_view(), name='messaging_email_get_template'),
    url(r'^templates/detail/$', DetailEmailTemplateView.as_view(), name='messaging_email_get_template'),

    # search
    url(r'^search/(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/(?P<search_key>.+)/$', EmailSearchView.as_view(), name='messaging_email_search'),
    url(r'^search/(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/$', EmailSearchView.as_view(), name='messaging_email_search'),
    url(r'^search/(?P<folder>[^/].+)/(?P<search_key>[^/].+)/$', EmailSearchView.as_view(), name='messaging_email_search_all'),
    url(r'^search/(?P<folder>[^/].+)/$', EmailSearchView.as_view(), name='messaging_email_search_all'),
    url(r'^search/$', ParseEmailTemplateView.as_view(), name='messaging_email_search_empty'),

    # email accounts
    url(r'^accounts/$', EmailAccountListView.as_view(), name='messaging_email_account_list'),
    url(r'^accounts/create/(?P<shared_with>[\d-]+)$', EmailAccountCreateView.as_view(), name='messaging_email_account_create'),
    url(r'^accounts/update/(?P<pk>[\d-]+)$', EmailAccountUpdateView.as_view(), name='messaging_email_account_update'),
    url(r'^accounts/delete/(?P<pk>[\d-]+)$', EmailAccountDeleteView.as_view(), name='messaging_email_account_delete'),
    url(r'^accounts/share/(?P<pk>[\d-]+)$', EmailAccountShareView.as_view(), name='messaging_email_account_share'),
    url(r'^accounts/unsubscribe/(?P<pk>[\d-]+)$', EmailAccountUnsubscribeView.as_view(), name='messaging_email_account_unsubscribe'),
)
