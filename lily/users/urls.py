from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from lily.utils.views import RedirectSetMessageView
from django.contrib import messages
from .views import (AcceptInvitationView, RegistrationView, ActivationView, ActivationResendView,
                    LoginView, DashboardView, SendInvitationView, APIAccessView)
from .forms import CustomPasswordResetForm, CustomSetPasswordForm


urlpatterns = patterns('',
    # Registration
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),

    # Activation
    url(r'^activation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', ActivationView.as_view(), name='activation'),
    url(r'^activation/resend/$', ActivationResendView.as_view(), name='activation_resend'),

    # Password reset
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {
            'template_name': 'users/password_reset/confirm.html',
            'set_password_form': CustomSetPasswordForm
        },
        name='password_reset_confirm'),
    url(r'^password_reset/$',
        'django.contrib.auth.views.password_reset',
        {
            'email_template_name': 'email/password_reset.email',
            'template_name': 'users/password_reset/form.html',
            'password_reset_form': CustomPasswordResetForm
        },
        name='password_reset'),
    url(r'^password_reset/done/$',
        RedirectSetMessageView.as_view(url=reverse_lazy('login'), message_level='info', message=_('I\'ve sent you an email, please check it to reset your password.')),
        name='password_reset_done'),
    url(r'^reset/complete/$',
        RedirectSetMessageView.as_view(url=reverse_lazy('login'), message_level='info', message=_('I\'ve reset your password, please login.')),
        name='password_reset_complete'),

    # Login
    url(r'^login/$', LoginView.as_view(), name='login'),

    # Invitations
    url(r'^invitation/invite/$', SendInvitationView.as_view(), name='invitation_invite'),
    url(r'^invitation/accept/(?P<first_name>.+)/(?P<email>.+)/(?P<tenant_id>[0-9]+)-(?P<date>[0-9]+)-(?P<hash>.+)/$', AcceptInvitationView.as_view(), name='invitation_accept'),

    # User profile settings
    url(r'^user/api/$', APIAccessView.as_view(), name='api_access_view'),

    # Dashboard and other user specific views, which require a logged in user
    url(r'^tag/(?P<tag>.+)/(?P<page>[0-9]+)/$', DashboardView.as_view(), name='dashboard_tag'),  # including tags and paging for microblog
    url(r'^tag/(?P<tag>.+)/$', DashboardView.as_view(), name='dashboard_tag'),  # including tags for microblog
    url(r'^(?P<page>[0-9]+)/$', DashboardView.as_view(), name='dashboard'),  # including paging for microblog
    # url(r'^$', DashboardView.as_view(), name='dashboard'),
)

# Views from django.contrib.auth.views
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout_then_login', name='logout'),
)
