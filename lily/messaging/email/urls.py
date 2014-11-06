from django.conf.urls import patterns, url

from lily.messaging.email.views import email_configuration_wizard, EmailMessageDetailView, EmailMessageHTMLView, \
    EmailInboxView, EmailSentView, EmailDraftsView, EmailTrashView, EmailSpamView, EmailFolderView, \
    EmailMessageCreateView, EmailMessageReplyView, EmailMessageForwardView, EmailAttachmentProxy, \
    MarkEmailMessageAsReadView, MarkEmailMessageAsUnreadView, TrashEmailMessageView, MoveEmailMessageView, \
    ListEmailTemplateView, CreateEmailTemplateView, UpdateEmailTemplateView, ParseEmailTemplateView, EmailSearchView, \
    EmailShareView, EmailAccountChangePasswordView, EmailAccountDeleteView, DeleteEmailTemplateView


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
    url(r'^templates/$', ListEmailTemplateView.as_view(), name='emailtemplate_list'),
    url(r'^templates/new/$', CreateEmailTemplateView.as_view(), name='emailtemplate_create'),
    url(r'^templates/update/(?P<pk>[\d-]+)/$', UpdateEmailTemplateView.as_view(), name='emailtemplate_update'),
    url(r'^templates/delete/(?P<pk>[\d-]+)/$', DeleteEmailTemplateView.as_view(), name='emailtemplate_delete'),
    url(r'^templates/parse/$', ParseEmailTemplateView.as_view(), name='messaging_email_template_parse'),

    # search
    url(r'^search/(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/(?P<search_key>.+)/$', EmailSearchView.as_view(), name='messaging_email_search'),
    url(r'^search/(?P<account_id>[\d-]+)/(?P<folder>[^/].+)/$', EmailSearchView.as_view(), name='messaging_email_search'),
    url(r'^search/(?P<folder>[^/].+)/(?P<search_key>[^/].+)/$', EmailSearchView.as_view(), name='messaging_email_search_all'),
    url(r'^search/(?P<folder>[^/].+)/$', EmailSearchView.as_view(), name='messaging_email_search_all'),
    url(r'^search/$', ParseEmailTemplateView.as_view(), name='messaging_email_search_empty'),

    # email account wizards
    url(r'^account/wizard/configuration/(?P<pk>[\w-]+)/$', email_configuration_wizard, name='messaging_email_account_wizard_template'),
    url(r'^account/wizard/share/(?P<pk>[\w-]+)/$', EmailShareView.as_view(), name='messaging_email_account_share_template'),

    # email account settings
    url(r'^account/(?P<pk>[\d-]+)/changepassword/$', EmailAccountChangePasswordView.as_view(), name='messaging_email_account_change_password'),
    url(r'^account/(?P<pk>[\d-]+)/delete/$', EmailAccountDeleteView.as_view(), name='messaging_email_account_delete'),

    # AJAX views
    # url(r'^history-list-json/(?P<pk>[\w-]+)/$', history_list_email_json_view, name='messaging_history_list_email_json'),

    # # e-mail account views
    # url(r'^account/edit/(?P<pk>[\w-]+)/$', edit_email_account_view, name='messaging_email_account_edit'),
    # # url(r'^account/details/(?P<pk>[\w-]+)/$', detail_email_account_view, name='messaging_email_account_details'),
)
