from django.conf.urls import patterns, url

from lily.messages.email.views import create_test_data_view, email_inbox_view, email_sent_view, email_draft_view, email_archive_view, create_email_account_view


urlpatterns = patterns('',
    url(r'^$', email_inbox_view, name='messages_email_inbox'),
    url(r'^sent/$', email_sent_view, name='messages_email_sent'),
    url(r'^drafts/$', email_draft_view, name='messages_email_drafts'),
    url(r'^archived/$', email_archive_view, name='messages_email_archived'),

    url(r'^account/new/$', create_email_account_view, name='messages_email_account_new'),

    url(r'^create-test-data/$', create_test_data_view, name='messages_email_create_test_data'),
)