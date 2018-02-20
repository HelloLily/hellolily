from django.conf.urls import url

from .views import AddAccountView, AddAccountCallbackView
from .views import HomeView, SyncView

urlpatterns = [
    # TESTVIEWS
    url(
        regex=r'^home/$',
        view=HomeView.as_view(),
        name='email_v3_homeview',
    ),
    url(
        regex=r'^home/(?P<account_id>[0-9]+)/$',
        view=HomeView.as_view(),
        name='email_v3_homeview',
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
