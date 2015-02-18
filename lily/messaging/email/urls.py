from django.conf.urls import patterns, url

from .views import (SetupEmailAuth, OAuth2Callback, EmailAttachmentProxy, EmailAccountListView, EmailAccountShareView,
                    EmailTemplateSetDefaultView, EmailTemplateGetDefaultView, EmailMessageHTMLView, EmailBaseView,
                    EmailAccountUpdateView, EmailAccountDeleteView, EmailTemplateListView, CreateEmailTemplateView,
                    UpdateEmailTemplateView, ParseEmailTemplateView, EmailMessageSendView, EmailTemplateDeleteView,
                    DetailEmailTemplateView)


urlpatterns = patterns(
    '',
    url(r'^setup/$', SetupEmailAuth.as_view(), name='messaging_email_account_setup'),
    url(r'^callback/$', OAuth2Callback.as_view(), name='gmail_callback'),
    url(r'^html/(?P<pk>[\d-]+)/$', EmailMessageHTMLView.as_view(), name='messaging_email_html'),
    url(r'^attachment/(?P<pk>[\d-]+)/$', EmailAttachmentProxy.as_view(), name='email_attachment_proxy_view'),

    # Account config
    url(r'^accounts/$', EmailAccountListView.as_view(), name='messaging_email_account_list'),
    url(r'^accounts/share/(?P<pk>[\d-]+)$', EmailAccountShareView.as_view(), name='messaging_email_account_share'),
    url(r'^accounts/update/(?P<pk>[\d-]+)$', EmailAccountUpdateView.as_view(), name='messaging_email_account_update'),
    url(r'^accounts/delete/(?P<pk>[\d-]+)$', EmailAccountDeleteView.as_view(), name='messaging_email_account_delete'),

    url(r'^attachment/(?P<pk>[\d-]+)/$', EmailAttachmentProxy.as_view(), name='email_attachment_proxy_view'),

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

    # compose views (create draft, reply, forward, preview)
    url(r'^compose/$', EmailMessageSendView.as_view(), name='messaging_email_compose'),
    url(r'^compose/(?P<pk>[\d-]+)/$', EmailMessageSendView.as_view(), name='messaging_email_compose'),
    # url(r'^reply/(?P<pk>[\d-]+)/$', EmailMessageReplyView.as_view(), name='messaging_email_reply'),
    # url(r'^forward/(?P<pk>[\d-]+)/$', EmailMessageForwardView.as_view(), name='messaging_email_forward'),

    url(r'^(?P<template_file>[\.\w-]+)/$', EmailBaseView.as_view(), name='messaging_email_inbox'),
    url(r'^$', EmailBaseView.as_view(), name='messaging_email_inbox'),
)
