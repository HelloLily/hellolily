from django.conf.urls import patterns, url

from lily.messages.email.views import create_test_data_view
from lily.messages.email.views import detail_email_inbox_view, detail_email_sent_view, detail_email_draft_view, detail_email_archive_view, detail_email_compose_view
from lily.messages.email.views import add_email_account_view, edit_email_account_view, detail_email_account_view
from lily.messages.email.views import add_email_template_view, edit_email_template_view, detail_email_template_view, parse_email_template_view


urlpatterns = patterns('',
    # Testing views
    url(r'^create-test-data/$', create_test_data_view, name='messages_email_create_test_data'),

    # E-mail views
    url(r'^$', detail_email_inbox_view, name='messages_email_inbox'),
    url(r'^sent/$', detail_email_sent_view, name='messages_email_sent'),
    url(r'^drafts/$', detail_email_draft_view, name='messages_email_drafts'),
    url(r'^archived/$', detail_email_archive_view, name='messages_email_archived'),
    url(r'^compose/$', detail_email_compose_view, name='messages_email_compose'),

    # E-mail account views
    url(r'^account/add/$', add_email_account_view, name='messages_email_account_add'),
    url(r'^account/edit/(?P<pk>[\w-]+)/$', edit_email_account_view, name='messages_email_account_edit'),
    url(r'^account/details/(?P<pk>[\w-]+)/$', detail_email_account_view, name='messages_email_account_details'),

    # E-mail template views
    url(r'^template/new/$', add_email_template_view, name='messages_email_template_add'),
    url(r'^template/edit/(?P<pk>[\w-]+)/$', edit_email_template_view, name='messages_email_template_edit'),
    url(r'^template/details/(?P<pk>[\w-]+)/$', detail_email_template_view, name='messages_email_template_details'),
    url(r'^template/parse/$', parse_email_template_view, name='messages_email_template_parse'),

)