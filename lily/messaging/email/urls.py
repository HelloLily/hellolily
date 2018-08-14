from django.conf.urls import url

from .views import (
    SetupEmailAuth, OAuth2Callback, EmailAttachmentProxy, EmailTemplateGetDefaultView, EmailMessageHTMLView,
    EmailTemplateListView, CreateEmailTemplateView, UpdateEmailTemplateView, ParseEmailTemplateView,
    EmailMessageSendView, EmailTemplateDeleteView, DetailEmailTemplateView, EmailMessageDraftView,
    EmailMessageReplyView, EmailMessageForwardView, EmailMessageReplyAllView, CreateTemplateVariableView,
    UpdateTemplateVariableView
)

urlpatterns = [
    url(r'^setup/$', SetupEmailAuth.as_view(), name='messaging_email_account_setup'),
    url(r'^callback/$', OAuth2Callback.as_view(), name='gmail_callback'),
    url(r'^html/(?P<pk>[\d-]+)/$', EmailMessageHTMLView.as_view(), name='messaging_email_html'),
    url(r'^attachment/(?P<pk>[\d-]+)/$', EmailAttachmentProxy.as_view(), name='email_attachment_proxy_view'),

    # Email templates
    url(r'^templates/$', EmailTemplateListView.as_view(), name='messaging_email_template_list'),
    url(r'^templates/create/$', CreateEmailTemplateView.as_view(), name='messaging_email_template_create'),
    url(
        r'^templates/update/(?P<pk>[\d-]+)/$',
        UpdateEmailTemplateView.as_view(),
        name='messaging_email_template_update'
    ),
    url(
        r'^templates/delete/(?P<pk>[\d-]+)/$',
        EmailTemplateDeleteView.as_view(),
        name='messaging_email_template_delete'
    ),
    url(r'^templates/parse/$', ParseEmailTemplateView.as_view(), name='messaging_email_template_parse'),
    url(
        r'^templates/get-default/(?P<account_id>[\d-]+)/$',
        EmailTemplateGetDefaultView.as_view(),
        name='messaging_email_template_get_default'
    ),
    url(
        r'^templates/get-default/$',
        EmailTemplateGetDefaultView.as_view(),
        name='messaging_email_template_get_default'
    ),
    url(
        r'^templates/detail/(?P<template_id>[\d-]+)/$',
        DetailEmailTemplateView.as_view(),
        name='messaging_email_get_template'
    ),
    url(r'^templates/detail/$', DetailEmailTemplateView.as_view(), name='messaging_email_get_template'),
    url(
        r'^templatevariables/create/$',
        CreateTemplateVariableView.as_view(),
        name='messaging_email_template_variables_create'
    ),
    url(
        r'^templatevariables/update/(?P<pk>[\d-]+)/$',
        UpdateTemplateVariableView.as_view(),
        name='messaging_email_template_variables_update'
    ),

    # Compose views (create draft, reply, forward, preview)
    url(r'^compose/$', EmailMessageSendView.as_view(), name='messaging_email_compose'),
    url(r'^compose/(?P<email_address>[^/]+)/$', EmailMessageSendView.as_view(), name='messaging_email_compose'),
    url(
        r'^compose/(?P<email_address>[^/]+)/(?P<template>[\d-]+)/$',
        EmailMessageSendView.as_view(),
        name='messaging_email_compose'
    ),
    url(r'^draft/$', EmailMessageDraftView.as_view(), name='messaging_email_draft'),
    url(r'^draft/(?P<pk>[\d-]+)/$', EmailMessageDraftView.as_view(), name='messaging_email_draft'),
    url(r'^reply/(?P<pk>[\d-]+)/$', EmailMessageReplyView.as_view(), name='messaging_email_reply'),
    url(r'^replyall/(?P<pk>[\d-]+)/$', EmailMessageReplyAllView.as_view(), name='messaging_email_reply_all'),
    url(r'^forward/(?P<pk>[\d-]+)/$', EmailMessageForwardView.as_view(), name='messaging_email_forward'),
]
