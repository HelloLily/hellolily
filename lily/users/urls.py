from django.conf.urls import patterns, url

from lily.users.forms import CustomPasswordResetForm
from lily.users.views import dashboard_view, login_view, registration_view, \
    activation_view, activation_resend_view, send_invitation_view, AcceptInvitationView, \
    password_reset_confirm_view


urlpatterns = patterns('',
    # Registration
    url(r'^registration/$', registration_view, name='registration'),
    
    # Activation
    url(r'^activation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', activation_view, name='activation'),
    url(r'^activation/resend/$', activation_resend_view, name='activation_resend'),
    
    # Password reset
    url(r'^password_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm_view, name='password_reset_confirm'),
    
    # Login
    url(r'^login/$', login_view, name='login'),
    
    # Invitations
    url(r'^invitation/invite/$', send_invitation_view, name='invitation_invite'),
    url(r'^invitation/accept/(?P<account_name>.+)/(?P<first_name>.+)/(?P<email>.+)/(?P<date>[0-9]+)-(?P<aidb36>[0-9A-Za-z]+)-(?P<hash>.+)/$', AcceptInvitationView.as_view(), name='invitation_accept'),
    
    # Dashboard and other user specific views, which require a logged in user
    url(r'^tag/(?P<tag>.+)/(?P<page>[0-9]+)/$', dashboard_view, name='dashboard_tag'), # including tags and paging for microblog
    url(r'^tag/(?P<tag>.+)/$', dashboard_view, name='dashboard_tag'), # including tags for microblog
    url(r'^(?P<page>[0-9]+)/$', dashboard_view, name='dashboard'), # including paging for microblog
    url(r'^$', dashboard_view, name='dashboard'),
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