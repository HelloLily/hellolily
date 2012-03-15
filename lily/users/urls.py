from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm

from lily.users.views import DashboardView, LoginView, RegistrationView, RegistrationSuccessView, \
                             ActivationView, ActivationResendView
from lily.users.forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = patterns('',
    # Registration
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),
    url(r'^registration/success/$', RegistrationSuccessView.as_view(), name='registration_success'),
    
    # Activation
    url(r'^activation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', ActivationView.as_view(), name='activation'),
    url(r'^activation/resend/$', ActivationResendView.as_view(), name='activation_resend'),
    
    # Login
    url(r'^login/$', LoginView.as_view(), name='login'),
    
    # Dashboard and other user specific views, which require a logged in user
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard'),
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