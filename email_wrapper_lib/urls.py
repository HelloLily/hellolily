from django.conf.urls import url

from .views import AddAccountView, AddAccountCallbackView, TestView

urlpatterns = [
    url(
        regex=r'^test$',
        view=TestView.as_view(),
        name='email_v3_testview',
    ),
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
