from lily.users.urls.password_reset import password_reset_urls
from lily.users.urls.registration import registration_urls
from lily.users.urls.two_factor_auth import auth_urls

urlpatterns = registration_urls + password_reset_urls + auth_urls
