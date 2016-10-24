from django.conf.urls import url
from lily.preferences.views.user import UserAccountView, UserProfileView


urlpatterns = [
    # Email preferences

    # Tenant preferences

    # User preferences
    url(r'^user/profile/$', UserProfileView.as_view(), name='user_profile_view'),
    url(r'^user/account/$', UserAccountView.as_view(), name='user_account_view'),
]
