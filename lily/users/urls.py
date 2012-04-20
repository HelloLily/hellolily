from django.conf.urls import patterns, url

from lily.users.forms import CustomPasswordResetForm, CustomSetPasswordForm
from lily.users.views import dashboard_view, login_view, registration_view, registration_success_view, \
    activation_view, activation_resend_view, send_invitation_view, AcceptInvitationView, \
    accept_invitation_view


urlpatterns = patterns('',
    # Registration
    url(r'^registration/$', registration_view, name='registration'),
    url(r'^registration/success/$', registration_success_view, name='registration_success'),
    
    # Activation
    url(r'^activation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', activation_view, name='activation'),
    url(r'^activation/resend/$', activation_resend_view, name='activation_resend'),
    
    # Login
    url(r'^login/$', login_view, name='login'),
    
    # Invitations
    url(r'^invitation/send/$', send_invitation_view, name='invitation_send'),
    url(r'^invitation/accept/(?P<account_name>.+)/(?P<first_name>.+)/(?P<email>.+)/(?P<date>[0-9]+)-(?P<aidb36>[0-9A-Za-z]+)-(?P<hash>.+)/$', AcceptInvitationView.as_view(), name='invitation_accept'),
    url(r'^invitation/success/$', accept_invitation_view, name='invitation_success'),
    
    # Dashboard and other user specific views, which require a logged in user
    url(r'^$', dashboard_view, name='dashboard'),
)

# Views from django.contrib.auth.views
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout_then_login', name='logout'),
    
    url(r'^password_reset/$', 'password_reset', {
        'template_name': 'users/password_reset.html',
        'password_reset_form': CustomPasswordResetForm,
    }, name='password_reset'),
                        
    url(r'^password_reset/done/$', 'password_reset_done', {
        'template_name': 'users/password_reset_done.html',
    }, name='password_reset_done'),
                        
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {
        'template_name': 'users/password_reset_confirm.html',
        'set_password_form': CustomSetPasswordForm,
    }, name='password_reset_confirm'),
    
    url(r'^reset/complete/$', 'password_reset_complete', {
        'template_name': 'users/password_reset_complete.html',
    }, name='password_reset_complete'),
)