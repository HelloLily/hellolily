from datetime import date, timedelta
from distutils.util import strtobool

import analytics
import chargebee
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, FormView
from django_otp.oath import totp
from django_otp.util import random_hex
from hashlib import sha256
from templated_email import send_templated_mail

from lily.messaging.email.credentials import get_credentials
from lily.messaging.email.models.models import EmailAccount
from lily.messaging.email.services import GmailService
from lily.users.models import LilyUser, UserInvite
from lily.users.registration.mixins import RegistrationMixin
from lily.utils.functions import guess_name_from_email
from .forms import (
    RegistrationAuthForm, RegistrationVerifyEmailForm, RegistrationProfileForm, RegistrationEmailAccountSetupForm,
    RegistrationConfirmationForm, RegistrationEmailAccountForm
)


class RegisterRedirectView(RedirectView):
    """
    View that automatically redirects to the appropriate registration step.
    """
    url_pattern = 'register_{}'

    def get_redirect_url(self, *args, **kwargs):
        if settings.REGISTRATION_SESSION_KEY not in self.request.session:
            return reverse('register_auth')

        return reverse(self.url_pattern.format(self.request.session[settings.REGISTRATION_SESSION_KEY]['step_name']))


class RegisterAuthView(RegistrationMixin, FormView):
    """
    View for the first step in the registration process.
    Either a user fills in their username/password or they authenticate using a social auth provider.
    """
    template_name = 'users/registration/auth.html'
    form_class = RegistrationAuthForm
    success_url = reverse_lazy('register_verify_email')
    step_name = 'auth'

    def get_initial(self):
        initial = super(RegisterAuthView, self).get_initial()

        if 'invitation_data' in self.request.session.get(settings.REGISTRATION_SESSION_KEY, {}):
            initial.update({
                'email': self.request.session[settings.REGISTRATION_SESSION_KEY]['invitation_data']['email']
            })

        return initial

    def get_context_data(self, **kwargs):
        context = super(RegisterAuthView, self).get_context_data(**kwargs)

        context['from_invite'] = 'invitation_data' in self.request.session.get(settings.REGISTRATION_SESSION_KEY, {})

        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data

        # If the user was invited, get the invitation data out of the session.
        invitation_data = self.request.session.get(settings.REGISTRATION_SESSION_KEY, {}).get('invitation_data', {})

        if invitation_data and invitation_data['email'] == cleaned_data['email']:
            # The user was invited and has chosen to register with the same email as they got the invite in.
            # This means we can skip the email address verification.
            user = LilyUser.objects.create_user(
                tenant_id=invitation_data['tenant_id'],
                first_name=invitation_data['first_name'],
                email=invitation_data['email'],
                password=cleaned_data['password']
            )

            # Because we don't call `authenticate` we need to set the authentication backend manually.
            user.backend = settings.AUTHENTICATION_MODEL_BACKEND

            # Log the new user in.
            login(self.request, user)

            # The email used by this user can no longer have valid invites, so delete them all.
            UserInvite.objects.filter(email=user.email).delete()

            # Send welcome mail to the new user.
            send_templated_mail(
                template_name='users/registration/email/welcome.email',
                recipient_list=[user.email, ],
                context={
                    'user': user,
                },
                from_email=settings.EMAIL_PERSONAL_HOST_USER,
                auth_user=settings.EMAIL_PERSONAL_HOST_USER,
                auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
            )

            return HttpResponseRedirect(reverse('register_profile'))

        else:
            # The user was not invited or has chosen to register with a different email address.
            # This means we will have to verify the address by sending a verification mail there.
            code = totp(random_hex(20), digits=6)  # Generate six digit code for validation.

            # Use the invite's first name or guess the first name from the given email address.
            first_name = invitation_data.get('first_name') or guess_name_from_email(cleaned_data['email'])[0]

            # Capitalize the first name, but only use it if it's more than one letter.
            first_name = first_name.capitalize() if len(first_name) > 1 else ''

            self.request.session[settings.REGISTRATION_SESSION_KEY]['auth_data'] = {
                'email': cleaned_data['email'],
                'password': cleaned_data['password'],
                'first_name': first_name,
                'code': code,
            }

            # Because we don't modify the session key, but a subkey the save is not done automatically.
            self.request.session.save()

            # Send welcome mail to the new user and include their email verification code.
            send_templated_mail(
                template_name='users/registration/email/welcome_with_verification.email',
                recipient_list=[cleaned_data['email'], ],
                context={
                    'first_name': first_name,
                    'code': code,
                },
                from_email=settings.EMAIL_PERSONAL_HOST_USER,
                auth_user=settings.EMAIL_PERSONAL_HOST_USER,
                auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
            )

        return HttpResponseRedirect(reverse('register_verify_email'))


class RegisterVerifyEmailView(RegistrationMixin, FormView):
    template_name = 'users/registration/email_verification.html'
    form_class = RegistrationVerifyEmailForm
    success_url = reverse_lazy('register_profile')
    step_name = 'verify_email'

    def get_context_data(self, **kwargs):
        context = super(RegisterVerifyEmailView, self).get_context_data(**kwargs)

        auth_data = self.request.session[settings.REGISTRATION_SESSION_KEY]['auth_data']
        context['email'] = auth_data['email']

        return context

    def get_form_kwargs(self):
        kwargs = super(RegisterVerifyEmailView, self).get_form_kwargs()

        auth_data = self.request.session[settings.REGISTRATION_SESSION_KEY]['auth_data']
        kwargs.update({
            'code': auth_data['code'],
        })

        return kwargs

    def form_valid(self, form):
        auth_data = self.request.session[settings.REGISTRATION_SESSION_KEY]['auth_data']

        # Create a new user instance with the given email and password.
        user = LilyUser.objects.create_user(
            first_name=auth_data['first_name'],
            email=auth_data['email'],
            password=auth_data['password']
        )

        # Because we don't call `authenticate` we need to set the authentication backend manually.
        user.backend = settings.AUTHENTICATION_MODEL_BACKEND

        # Log the new user in.
        login(self.request, user)

        # The email used by this user can no longer have valid invites, so delete them all.
        # It can be that the user was invited but chose to register with a different email.
        # In that case we also want to delete invitations sent to the originally invited email.
        invitation_data = self.request.session.get(settings.REGISTRATION_SESSION_KEY, {}).get('invitation_data', {})

        if invitation_data:
            UserInvite.objects.filter(email__in=[user.email, invitation_data['email'], ]).delete()
        else:
            UserInvite.objects.filter(email=user.email).delete()

        return super(RegisterVerifyEmailView, self).form_valid(form)


class RegisterProfileView(RegistrationMixin, FormView):
    """
    View for the second step in the registration process.
    The user must enter or verify the profile information.
    """
    template_name = 'users/registration/profile.html'
    form_class = RegistrationProfileForm
    success_url = reverse_lazy('register_email_account_setup')
    step_name = 'profile'

    def __init__(self, **kwargs):
        super(RegisterProfileView, self).__init__(**kwargs)

        self.first_user = LilyUser.objects.all().count() == 1

    def get_form_kwargs(self):
        kwargs = super(RegisterProfileView, self).get_form_kwargs()

        # Only show the tenant fields if this is the first registered user for this tenant.
        kwargs['show_tenant_fields'] = self.first_user

        return kwargs

    def get_initial(self):
        initial = super(RegisterProfileView, self).get_initial()

        initial.update({
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'company_name': self.request.user.tenant.name,
            'country': self.request.user.tenant.country,
        })

        return initial

    def form_valid(self, form):
        cleaned_data = form.cleaned_data

        user = self.request.user
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.save()

        tenant = user.tenant
        if self.first_user:
            tenant.name = cleaned_data['company_name']
            tenant.country = cleaned_data['country']
            tenant.save()

        if settings.BILLING_ENABLED:
            subscription_id = tenant.billing.subscription_id
            if subscription_id:
                chargebee.Subscription.update(subscription_id, {
                    'customer': {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'company': tenant.name,
                    },
                })

        return super(RegisterProfileView, self).form_valid(form)


class RegisterEmailAccountSetupView(RegistrationMixin, FormView):
    """
    The user must determine whether or not to add an email account.
    """
    template_name = 'users/registration/email_account_setup.html'
    form_class = RegistrationEmailAccountSetupForm
    success_url = reverse_lazy('messaging_email_account_setup')
    step_name = 'email_account_setup'


class RegisterEmailAccountDetailsView(RegistrationMixin, FormView):
    template_name = 'users/registration/email_account_details.html'
    form_class = RegistrationEmailAccountForm
    # success_url = reverse_lazy('register_autofill')  # This is for when we have autofill.
    success_url = reverse_lazy('register_done')
    step_name = 'email_account_details'

    def get_initial(self):
        initial = super(RegisterEmailAccountDetailsView, self).get_initial()

        # Set the email account on self, so the query is not executed twice on form submit.
        self.email_account = self.request.user.email_accounts_owned.first()

        initial.update({
            'from_name': self.request.user.full_name,
            'label': self.email_account.email_address,
            'label_color': '#2ab8e0',
            'privacy': EmailAccount.READ_ONLY,
            'only_new': False,
        })

        return initial

    def form_valid(self, form):
        cleaned_data = form.cleaned_data

        self.email_account.from_name = cleaned_data['from_name']
        self.email_account.label = cleaned_data['label']
        self.email_account.privacy = cleaned_data['privacy']
        self.email_account.only_new = bool(strtobool(cleaned_data['only_new']))
        self.email_account.is_authorized = True

        if self.email_account.only_new:
            # When the user only wants to synchronize only new email messages, retrieve the history id of the email
            # account. That history id is used for the successive (history) sync to retrieve only the changes starting
            # from this moment.
            credentials = get_credentials(self.email_account)

            # Setup service to retrieve history id from Google.
            gmail_service = GmailService(credentials)
            profile = gmail_service.execute_service(gmail_service.service.users().getProfile(userId='me'))

            self.email_account.history_id = profile.get('historyId')
            self.email_account.is_syncing = False

        self.email_account.save()

        return super(RegisterEmailAccountDetailsView, self).form_valid(form)


# class RegisterAutofillView(RegistrationMixin, FormView):
#     """
#     The user must determine whether or not lily should autofill contacts/accounts based on their email messages.
#     """
#     template_name = 'users/registration/step_5_autofill.html'
#     form_class = RegistrationAutofillForm
#     success_url = reverse_lazy('register_done')
#     step_name = 'autofill'


class RegisterDoneView(RegistrationMixin, FormView):
    """
    Display a pretty confirmation screen to the user and redirect them to the app afterwards.
    """
    template_name = 'users/registration/done.html'
    form_class = RegistrationConfirmationForm
    success_url = reverse_lazy('base_view')
    step_name = 'done'

    def form_valid(self, form):
        # Track registration finished in Segment.
        plan = None
        try:
            plan = self.request.user.tenant.billing.plan
        except AttributeError:
            pass

        registration_type = 'Organic'
        if not self.request.user.has_usable_password():
            registration_type = 'Social'
        elif 'invitation_data' in self.request.session[settings.REGISTRATION_SESSION_KEY]:
            registration_type = 'Invite'

        analytics.track(
            self.request.user.id,
            'registration-finished', {
                'type': registration_type,
                'plan_id': plan.id if plan else '',
                'plan_tier': plan.tier if plan else '',
                'plan_name': plan.name if plan else '',
                'is_free_plan': self.request.user.tenant.billing.is_free_plan,
                'tanant_id': self.request.user.tenant.id,
                'tanant_name': self.request.user.tenant.name,
            },
            anonymous_id='Anonymous' if self.request.user.is_anonymous() else None
        )

        return super(RegisterDoneView, self).form_valid(form)


class AcceptInvitationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.link_is_valid(*args, **kwargs):
            if settings.REGISTRATION_SESSION_KEY not in self.request.session:
                # If there is no registration session yet, initialize it.
                self.request.session[settings.REGISTRATION_SESSION_KEY] = {}

            # Set the invitation data on the session.
            self.request.session[settings.REGISTRATION_SESSION_KEY]['step'] = 1
            self.request.session[settings.REGISTRATION_SESSION_KEY]['invitation_data'] = {
                'email': kwargs['email'],
                'first_name': kwargs['first_name'],
                'tenant_id': kwargs['tenant_id'],
            }

            # Because we don't modify the session key but a subkey, the save is not done automatically.
            self.request.session.save()

            return reverse('register_auth')
        else:
            messages.error(self.request, 'This invitation link is invalid or expired')
            return reverse('login')

    def link_is_valid(self, *args, **kwargs):
        """
        This functions performs all checks to verify the url is correct.
        Returns:
            Boolean: True if link is valid
        """
        email = kwargs['email']
        first_name = kwargs['first_name']
        tenant_id = kwargs['tenant_id']
        datestring = kwargs['date']
        sha256_hash = kwargs['hash']

        # Check if a user with the email address already exists, if it does this invitation is invalid.
        if LilyUser.objects.filter(email__iexact=email).exists():
            return False

        invite_id = UserInvite.objects.filter(
            email__iexact=email,
            first_name=first_name
        ).values_list('id', flat=True).first()

        sha_input = '{}-{}-{}-{}-{}'.format(
            tenant_id,
            invite_id,
            email,
            datestring,
            settings.SECRET_KEY
        )
        correct_hash = sha256(sha_input).hexdigest()

        if not invite_id or not sha256_hash == correct_hash or not len(datestring) == 8:
            # There should always be an invite object from the database.
            # The hash should always be correct.
            # The date should always be a string of 8 characters.
            return False

        today = date.today()
        try:
            # Check if it is a valid date.
            dateobj = date(int(datestring[4:8]), int(datestring[2:4]), int(datestring[:2]))
        except ValueError:
            return False

        if (today < dateobj) or ((today - timedelta(days=settings.USER_INVITATION_TIMEOUT_DAYS)) > dateobj):
            # The link must not be too old and not from the future.
            return False

        # Every check was passed successfully, link is valid.
        return True
