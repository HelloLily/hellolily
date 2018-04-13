from django.conf.urls import url
from two_factor.views import QRGeneratorView

from .views import TwoFactorSetupView, TwoFactorPhoneSetupView


urlpatterns = [
    url(
        regex=r'^setup/$',
        view=TwoFactorSetupView.as_view(),
        name='setup',
    ),
    url(
        regex=r'^qrcode/$',
        view=QRGeneratorView.as_view(),
        name='qr_code',
    ),
    url(
        regex=r'^backup/phone/register/$',
        view=TwoFactorPhoneSetupView.as_view(),
        name='phone_create',
    ),
]
