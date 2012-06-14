from django.conf.urls import patterns, url

from lily.messages.views import dashboard_view, message_list_view


urlpatterns = patterns('',
    url(r'^$', dashboard_view, name='messages_dashboard'),
    url(r'^sent/$', dashboard_view, name='messages_sent'),
    url(r'^drafts/$', dashboard_view, name='messages_drafts'),
    url(r'^archived/$', dashboard_view, name='messages_archived'),
    
    url(r'^get-message-list/$', message_list_view, name='messages_archived'),
)