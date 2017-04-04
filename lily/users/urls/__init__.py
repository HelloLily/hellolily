from .password_reset import password_reset_urls
from .registration import registration_urls
from .two_factor_auth import auth_urls


urlpatterns = password_reset_urls + registration_urls + auth_urls
