from django.conf.urls import patterns, url

from lily.contacts.views import add_contact_view, edit_contact_view, \
    delete_contact_view, edit_function_view, list_contact_view, detail_contact_view

urlpatterns = patterns('',
     url(r'^add/$', add_contact_view, name='contact_add'),
     url(r'^functions/(?P<pk>[\w-]+)/$', edit_function_view, name='function_edit'),
     url(r'^edit/(?P<pk>[\w-]+)/$', edit_contact_view, name='contact_edit'),
     url(r'^details/(?P<pk>[\w-]+)/$', detail_contact_view, name='contact_details'),
     url(r'^delete/xhr/(?P<pk>[\w-]+)/$', delete_contact_view, name='contact_delete'),
     url(r'^$', list_contact_view, name='contact_list'),
)