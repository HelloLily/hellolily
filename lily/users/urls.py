from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm

from lily.users.views import DashboardView, LoginView, RegistrationView, RegistrationSuccessView
from lily.users.forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = patterns('',
    # Registration
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),
    url(r'^registration/success/$', RegistrationSuccessView.as_view(), name='registration_success'),
    
    # Activation
    #url(r'^activation/$', RegistrationSuccessView.as_view(), name='registration_success'),
    #url(r'^activation/success/$', RegistrationSuccessView.as_view(), name='registration_success'),
    #url(r'^activation/resend/$', RegistrationSuccessView.as_view(), name='registration_success'),
    
    # Login
    url(r'^login/$', LoginView.as_view(), name='login'),
    
    # 
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard'),
)

# Views from django.contrib.auth.views
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'next_page': '/login/?logged_out=true'}, name='logout'),
    
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
        'post_reset_redirect': '/login/?password_reset=true'
    }, name='password_reset_confirm'),
)