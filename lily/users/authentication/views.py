from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetConfirmView, INTERNAL_RESET_URL_TOKEN
from django.shortcuts import redirect, resolve_url
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import RedirectView
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from oauthlib.oauth2 import OAuth2Error
from templated_email import send_templated_mail
from two_factor import signals
from two_factor.forms import BackupTokenForm
from two_factor.views import LoginView
from two_factor.views.utils import class_view_decorator

from lily.users.authentication.social_auth.helpers import get_authorization_url, get_profile
from lily.users.models import LilyUser
from lily.users.two_factor_auth.forms import CustomAuthenticationTokenForm

from .forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm


@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
class CustomLoginView(LoginView):
    template_name = 'users/authentication/login.html'
    form_list = (
        ('auth', CustomAuthenticationForm),
        ('token', CustomAuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def dispatch(self, request, *args, **kwargs):
        """
        If user is authenticated, redirect to the homepage.
        """
        redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')

        #  Prevent redirects to files, since that can be used to extrapolate auth status by 3rd parties.
        blocked_redirects = [settings.STATIC_URL, settings.MEDIA_URL, reverse('favicon'), ]
        if any([redirect_to.startswith(blocked) for blocked in blocked_redirects]):
            redirect_to = '/'
            request.GET = request.GET.copy()
            request.GET[REDIRECT_FIELD_NAME] = redirect_to

        if request.method == 'GET' and request.user.is_authenticated and request.path == settings.LOGIN_URL:
            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, allowed_hosts={request.get_host()}, require_https=True):
                redirect_to = reverse('base_view')

            return http.HttpResponseRedirect(redirect_to)

        return super(CustomLoginView, self).dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        login(self.request, self.get_user())

        if not self.request.user.info.registration_finished:
            # If the user has not finished registration yet, redirect them there to finish it now.
            redirect_to = reverse('register')
        else:
            redirect_to = self.request.POST.get(
                self.redirect_field_name,
                self.request.GET.get(self.redirect_field_name, '')
            )
            if not is_safe_url(url=redirect_to, host=self.request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        device = getattr(self.get_user(), 'otp_device', None)

        if device:
            if isinstance(device, StaticDevice):
                # User logged in using a static backup code, refresh it with a new one.
                device.token_set.create(token=StaticToken.random_token())

            signals.user_verified.send(
                sender=__name__,
                request=self.request,
                user=self.get_user(),
                device=device
            )

        return redirect(redirect_to)


@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
class SocialAuthView(RedirectView):
    provider_name = None

    def get(self, request, *args, **kwargs):
        self.provider_name = kwargs['provider_name']

        return super(SocialAuthView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return get_authorization_url(self.request, self.provider_name)


@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
@class_view_decorator(csrf_exempt)
class SocialAuthCallbackView(RedirectView):
    provider_name = None

    def get(self, request, *args, **kwargs):
        self.provider_name = kwargs['provider_name']

        return super(SocialAuthCallbackView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        try:
            profile = get_profile(self.request, self.provider_name)
        except OAuth2Error:
            messages.error(self.request, 'Unable to get access to your account, please try again.')
            return reverse('login')

        # Authenticate the user using their email.
        user = authenticate(self.request, social_username=profile['email'])
        if user:
            # User was authenticated, so do a login.
            login(self.request, user)

            return reverse('base_view')
        elif not LilyUser.all_objects.filter(email=profile['email'].lower()).exists():
            # There is no record of a user with this email address, so we create it.
            user = LilyUser.objects.create_user(**profile)

            # Because we don't call `authenticate` we need to set the authentication backend manually.
            user.backend = settings.AUTHENTICATION_SOCIAL_BACKEND

            # Log the new user in.
            login(self.request, user)

            # Send welcome mail to the new user.
            send_templated_mail(
                template_name='users/registration/email/welcome.email',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email, ],
                context={
                    'user': user,
                }
            )

            return reverse('register_profile')
        else:
            # User is inactive, handle it.
            messages.error(self.request, _('This account is inactive.'))
            return reverse('login')


class CustomLogoutView(LogoutView):
    next_page = 'login'


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'users/authentication/email/password_reset.email'
    extra_email_context = None
    form_class = CustomPasswordResetForm
    from_email = settings.DEFAULT_FROM_EMAIL
    success_url = reverse_lazy('login')
    template_name = 'users/authentication/password_reset.html'

    def get_initial(self):
        """
        Copy the email from the GET parameters for initial value.
        If a user fills their email on the login form, then it's also sent to this view after clicking the link.
        """
        initial = super(CustomPasswordResetView, self).get_initial()
        initial['email'] = self.request.GET.get('email', '')

        return initial

    def form_valid(self, form):
        messages.info(self.request, _('I\'ve sent you an email, please check it to reset your password.'))

        return super(CustomPasswordResetView, self).form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    post_reset_login = False
    success_url = reverse_lazy('login')
    template_name = 'users/authentication/password_reset_confirm.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        """
        Redirect to the login page with a message if the token is incorrect, instead of showing a page with a message.
        """
        user = self.get_user(kwargs['uidb64'])
        token = kwargs['token']

        if not token == INTERNAL_RESET_URL_TOKEN and not self.token_generator.check_token(user, token):
            redirect_url = reverse('login')
            messages.error(
                self.request,
                'The link was invalid, possibly because it has already been used. Please request a new password reset.'
            )

            return http.HttpResponseRedirect(redirect_url)

        return super(CustomPasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.info(self.request, _('I\'ve reset your password for you, go ahead and login.'))

        return super(CustomPasswordResetConfirmView, self).form_valid(form)
