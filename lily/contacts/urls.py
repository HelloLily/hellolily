from django.conf.urls import patterns, url

from lily.contacts.views import add_contact_view, edit_contact_view, delete_contact_view, \
    list_contact_view, detail_contact_view, ConfirmContactEmailView, json_contact_works_at_view, JsonContactListView


urlpatterns = patterns('',
    url(r'^add/$', add_contact_view, name='contact_add'),
    url(r'^edit/(?P<pk>[\w-]+)/$', edit_contact_view, name='contact_edit'),
    url(r'^details/(?P<pk>[\w-]+)/$', detail_contact_view, name='contact_details'),
    url(r'^json_works_at/(?P<pk>[\w-]+)/$', json_contact_works_at_view, name='json_contact_works_at'),
    url(r'^delete/xhr/(?P<pk>[\w-]+)/$', delete_contact_view, name='contact_delete'),
    url(r'^confirm-email/(?P<data>.+)/$', ConfirmContactEmailView.as_view(), name='contact_confirm_email'),
    url(r'^json_list/$', JsonContactListView.as_view(), name='json_contact_list'),
    url(r'^tag/(?P<tag>[\w-]+)/$', list_contact_view, name='contact_list_filtered_by_tag'),
    url(r'^(?P<b36_pks>[\w;]*)/$', list_contact_view, name='contact_list_filtered'),
    url(r'^$', list_contact_view, name='contact_list'),
)
