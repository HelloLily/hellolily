from django.conf.urls import patterns, url

from lily.cases.views import detail_case_view, list_case_view, add_case_view, edit_case_view, \
    delete_case_view


urlpatterns = patterns('',
    url(r'^add/$', add_case_view, name='case_add'),
    url(r'^edit/(?P<pk>[\w-]+)/$', edit_case_view, name='case_edit'),
    url(r'^details/(?P<pk>[\w-]+)/$', detail_case_view, name='case_details'),
    url(r'^delete/xhr/(?P<pk>[\w-]+)/$', delete_case_view, name='case_delete'),
    url(r'^$', list_case_view, name='case_list'),
)