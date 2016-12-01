from django.conf.urls import url
from lily.preferences.views.user import UserAccountView


urlpatterns = [
    # Email preferences

    # Tenant preferences

    # User preferences
    url(r'^user/account/$', UserAccountView.as_view(), name='user_account_view'),
]
