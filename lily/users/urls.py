from django.conf.urls import patterns, url

from .forms import CustomPasswordResetForm
from .views import (AcceptInvitationView, RegistrationView, ActivationView, ActivationResendView,
                    CustomSetPasswordView, LoginView, DashboardView, UserProfileView, UserAccountView,
                    SendInvitationView, APIAccessView)


urlpatterns = patterns('',
    # Registration
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),

    # Activation
    url(r'^activation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', ActivationView.as_view(), name='activation'),
    url(r'^activation/resend/$', ActivationResendView.as_view(), name='activation_resend'),

    # Password reset
    url(r'^password_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', CustomSetPasswordView.as_view(), name='password_reset_confirm'),

    # Login
    url(r'^login/$', LoginView.as_view(), name='login'),

    # Invitations
    url(r'^invitation/invite/$', SendInvitationView.as_view(), name='invitation_invite'),
    url(r'^invitation/accept/(?P<first_name>.+)/(?P<email>.+)/(?P<tenant_id>[0-9]+)-(?P<date>[0-9]+)-(?P<hash>.+)/$', AcceptInvitationView.as_view(), name='invitation_accept'),

    # User profile settings
    url(r'^user/profile/$', UserProfileView.as_view(), name='user_profile_view'),
    url(r'^user/account/$', UserAccountView.as_view(), name='user_account_view'),
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

    url(r'^password_reset/$', 'password_reset', {
        'template_name': 'users/password_reset/form.html',
        'password_reset_form': CustomPasswordResetForm,
    }, name='password_reset'),

    url(r'^password_reset/done/$', 'password_reset_done', {
        'template_name': 'users/password_reset/done.html',
    }, name='password_reset_done'),

    url(r'^reset/complete/$', 'password_reset_complete', {
        'template_name': 'users/password_reset/complete.html',
    }, name='password_reset_complete'),
)
