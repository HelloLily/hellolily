from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import password_reset_confirm, password_reset, logout_then_login
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from lily.utils.views import RedirectSetMessageView
from .views import (AcceptInvitationView, RegistrationView, ActivationView, ActivationResendView, LoginView,
                    SendInvitationView)
from .forms import CustomPasswordResetForm, CustomSetPasswordForm


urlpatterns = [
    # Registration
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),

    # Activation
    url(r'^activation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', ActivationView.as_view(), name='activation'),
    url(r'^activation/resend/$', ActivationResendView.as_view(), name='activation_resend'),

    # Password reset
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        {
            'template_name': 'users/password_reset/confirm.html',
            'set_password_form': CustomSetPasswordForm
        },
        name='password_reset_confirm'),
    url(r'^password_reset/$',
        password_reset,
        {
            'email_template_name': 'email/password_reset.email',
            'template_name': 'users/password_reset/form.html',
            'password_reset_form': CustomPasswordResetForm,
            'from_email': settings.DEFAULT_FROM_EMAIL,
        },
        name='password_reset'),
    url(r'^password_reset/done/$',
        RedirectSetMessageView.as_view(url=reverse_lazy('login'),
                                       message_level='info',
                                       message=_('I\'ve sent you an email, please check it to reset your password.'),
                                       permanent=False),
        name='password_reset_done'),
    url(r'^reset/complete/$',
        RedirectSetMessageView.as_view(url=reverse_lazy('login'),
                                       message_level='info',
                                       message=_('I\'ve reset your password, please login.'),
                                       permanent=False),
        name='password_reset_complete'),

    # Login
    url(r'^login/$', LoginView.as_view(), name='login'),

    # Invitations
    url(r'^invitation/invite/$', SendInvitationView.as_view(), name='invitation_invite'),
    url(r'^invitation/accept/(?P<first_name>.+)/(?P<email>.+)/(?P<tenant_id>[0-9]+)-(?P<date>[0-9]+)-(?P<hash>.+)/$',
        AcceptInvitationView.as_view(),
        name='invitation_accept'),
]

# Views from django.contrib.auth.views
urlpatterns += [
    url(r'^logout/$', logout_then_login, name='logout'),
]
