from django.conf.urls import url

from .social_auth.helpers import SOCIAL_AUTH_PROVIDERS
from .views import (
    CustomLoginView, SocialAuthView, SocialAuthCallbackView, CustomLogoutView,
    CustomPasswordResetView, CustomPasswordResetConfirmView
)


urlpatterns = [
    url(
        regex=r'^login/$',
        view=CustomLoginView.as_view(),
        name='login',
    ),
    url(
        regex=r'^social/login/(?P<provider_name>{})/$'.format('|'.join(SOCIAL_AUTH_PROVIDERS.keys())),
        view=SocialAuthView.as_view(),
        name='social_login',
    ),
    url(
        regex=r'^social/callback/(?P<provider_name>{})/$'.format('|'.join(SOCIAL_AUTH_PROVIDERS.keys())),
        view=SocialAuthCallbackView.as_view(),
        name='social_login_callback',
    ),
    url(
        regex=r'^logout/$',
        view=CustomLogoutView.as_view(),
        name='logout',
    ),
    url(
        regex=r'^password-reset/$',
        view=CustomPasswordResetView.as_view(),
        name='password_reset',
    ),
    url(
        regex=r'^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
]
