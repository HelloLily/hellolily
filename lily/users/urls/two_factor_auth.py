from django.conf.urls import url
from django.contrib.auth.views import logout_then_login

from two_factor.views import QRGeneratorView

from lily.users.views.two_factor_auth import (
    TwoFactorLoginView, TwoFactorSetupView, TwoFactorPhoneSetupView
)

auth_urls = [
    url(
        regex=r'^login/$',
        view=TwoFactorLoginView.as_view(),
        name='login',
    ),
    url(
        regex=r'^logout/$',
        view=logout_then_login,
        name='logout',
    ),
    url(
        regex=r'^two-factor/setup/$',
        view=TwoFactorSetupView.as_view(),
        name='setup',
    ),
    url(
        regex=r'^two-factor/qrcode/$',
        view=QRGeneratorView.as_view(),
        name='qr_code',
    ),
    url(
        regex=r'^two-factor/backup/phone/register/$',
        view=TwoFactorPhoneSetupView.as_view(),
        name='phone_create',
    ),
]
