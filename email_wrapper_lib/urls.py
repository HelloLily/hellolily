from django.conf.urls import url

from .views import AddAccountView, AddAccountCallbackView
from .views import MessagesView, SyncView

urlpatterns = [
    # TESTVIEWS
    url(
        regex=r'^messages/$',
        view=MessagesView.as_view(),
        name='email_v3_messagesview',
    ),
    url(
        regex=r'^messages/(?P<account_id>[0-9]+)/$',
        view=MessagesView.as_view(),
        name='email_v3_messagesview',
    ),
    url(
        regex=r'^messages/(?P<folder_id>[\w]+)/$',
        view=MessagesView.as_view(),
        name='email_v3_messagesview',
    ),
    url(
        regex=r'^messages/(?P<account_id>[0-9]+)/(?P<folder_id>[\w]+)/$',
        view=MessagesView.as_view(),
        name='email_v3_messagesview',
    ),
    url(
        regex=r'^sync/$',
        view=SyncView.as_view(),
        name='email_v3_syncview',
    ),
    url(
        regex=r'^sync/(?P<account_id>[\d]+)/$',
        view=SyncView.as_view(),
        name='email_v3_syncview',
    ),

    # REGULAR VIEWS
    url(
        regex=r'^account/add/(?P<provider_name>[\w]+)/$',
        view=AddAccountView.as_view(),
        name='email_v3_account_add',
    ),
    url(
        regex=r'^account/callback/(?P<provider_name>[\w]+)/$',
        view=AddAccountCallbackView.as_view(),
        name='email_v3_account_add_callback',
    ),
]
