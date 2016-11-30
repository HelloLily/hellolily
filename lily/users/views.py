from datetime import date, timedelta
from hashlib import sha256

import anyjson
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import login
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View, TemplateView, FormView
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import ugettext_lazy as _
from extra_views import FormSetView
from templated_email import send_templated_mail


from lily.utils.functions import is_ajax, post_intercom_event

from .forms import (CustomAuthenticationForm, RegistrationForm, ResendActivationForm, InvitationForm,
                    InvitationFormset, UserRegistrationForm)
from .models import LilyUser


class RegistrationView(FormView):
    """
    This view shows and handles the registration form, when valid register a new user.
    """
    template_name = 'users/registration.html'
    form_class = RegistrationForm

    def get(self, request, *args, **kwargs):
        # Show a different template when registration is closed.
        if settings.REGISTRATION_POSSIBLE:
            return super(RegistrationView, self).get(request, args, kwargs)
        else:
            self.template_name = 'users/registration_closed.html'
            return self.render_to_response({})

    def form_valid(self, form):
        """
        Register a new user.
        """
        # Do not accept any valid form when registration is closed.
        if not settings.REGISTRATION_POSSIBLE:
            messages.error(self.request, _('I\'m sorry, but I can\'t let anyone register at the moment.'))
            return redirect(reverse_lazy('login'))

        # Create and save user
        user = LilyUser.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            position=form.cleaned_data['position']
        )

        user.is_active = False
        user.save()

        # Add to admin group
        account_admin = Group.objects.get_or_create(name='account_admin')[0]
        user.groups.add(account_admin)

        # Get the current site
        try:
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            current_site = ''

        # Generate uidb36 and token for the activation link
        uidb36 = int_to_base36(user.pk)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)

        # Send an activation mail
        # TODO: only create/save contact when email sent successfully
        send_templated_mail(
            template_name='activation',
            recipient_list=[form.cleaned_data['email']],
            context={
                'current_site': current_site,
                'protocol': self.request.is_secure() and 'https' or 'http',
                'user': user,
                'uidb36': uidb36,
                'token': token,
            },
            from_email=settings.EMAIL_PERSONAL_HOST_USER,
            auth_user=settings.EMAIL_PERSONAL_HOST_USER,
            auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
        )

        # Show registration message
        messages.success(
            self.request,
            _('Registration completed. I\'ve sent you an email, please check it to activate your account.')
        )

        return self.get_success_url()

    def get_success_url(self):
        """
        Redirect to the success url.
        """
        return redirect(reverse_lazy('login'))


class ActivationView(TemplateView):
    """
    This view checks whether the activation link is valid and acts accordingly.
    """
    # Template is only shown when something went wrong
    template_name = 'users/activation_failed.html'
    token_generator = PasswordResetTokenGenerator()

    def get(self, request, *args, **kwargs):
        """
        Check whether the activation link is valid, for this both the user id and the token should
        be valid. Messages are shown when user belonging to the user id is already active
        and when the account is successfully activated. In all other cases the activation failed
        template is shown.
        Finally if the user is successfully activated, log user in and redirect to their dashboard.
        """
        try:
            user_id = base36_to_int(kwargs['uidb36'])
            user = LilyUser.objects.get(id=user_id)
            token = kwargs['token']
        except (ValueError, LilyUser.DoesNotExist):
            # Show template as per normal TemplateView behaviour
            return TemplateView.get(self, request, *args, **kwargs)

        if self.token_generator.check_token(user, token):
            # Show activation message
            messages.info(request, _('I\'ve activated your account, please login.'))
        else:
            # Show template as per normal TemplateView behaviour
            return TemplateView.get(self, request, *args, **kwargs)

        # Set is_active to True and save the user
        user.is_active = True
        user.save()

        # Redirect to dashboard
        return redirect(reverse_lazy('login'))


class ActivationResendView(FormView):
    """
    This view is used by an user to request a new activation email.
    """
    template_name = 'users/activation_resend_form.html'
    form_class = ResendActivationForm

    def form_valid(self, form):
        """
        If ResendActivationForm passed the validation, generate new token and send an email.
        """
        token_generator = PasswordResetTokenGenerator()
        users = LilyUser.objects.filter(
            email__iexact=form.cleaned_data['email']
        )

        # Get the current site or empty string
        try:
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            current_site = ''

        for user in users:
            # Generate uidb36 and token for the activation link
            uidb36 = int_to_base36(user.pk)
            token = token_generator.make_token(user)

            # Email to the user
            send_templated_mail(
                template_name='activation',
                recipient_list=[form.cleaned_data['email']],
                context={
                    'current_site': current_site,
                    'protocol': self.request.is_secure() and 'https' or 'http',
                    'user': user,
                    'uidb36': uidb36,
                    'token': token,
                },
                from_email=settings.EMAIL_PERSONAL_HOST_USER,
                auth_user=settings.EMAIL_PERSONAL_HOST_USER,
                auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
            )

        # Show registration message
        messages.success(
            self.request,
            _('Reactivation successful. I\'ve sent you an email, please check it to activate your account.')
        )

        # Redirect to success url
        return self.get_success_url()

    def get_success_url(self):
        """
        Redirect to the success url.
        """
        return redirect(reverse_lazy('login'))


class LoginView(View):
    """
    This view extends the default login view with a 'remember me' feature.
    """
    template_name = 'users/login_form.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user wants to be remembered and return the default login view.
        """
        if request.user.is_authenticated():
            return redirect(reverse_lazy('base_view'))

        if request.method == 'POST':
            # If not using 'remember me' feature use default expiration time.
            if not request.POST.get('remember_me', False):
                request.session.set_expiry(None)
        return login(
            request,
            template_name=self.template_name,
            authentication_form=CustomAuthenticationForm,
            *args,
            **kwargs
        )


class SendInvitationView(FormSetView):
    """
    This view is used to invite new people to the site. It works with a formset to allow easy
    adding of multiple invitations. It also checks whether the call is done via ajax or via a normal
    form, to use ajax append ?xhr to the url.
    """
    template_name = 'users/invitation/invitation_form.html'
    form_template_name = 'utils/templates/formset_invitation.html'
    form_class = InvitationForm
    formset_class = InvitationFormset
    extra = 1
    can_delete = True

    def formset_valid(self, formset):
        """
        This function is called when the formset is deemed valid.
        An email is sent to all email fields which are filled in.
        If the request is done via ajax give json back with a success message, otherwise
        redirect to the success url.
        """
        protocol = self.request.is_secure() and 'https' or 'http'
        date_string = date.today().strftime('%d%m%Y')

        # Get the current site or empty string
        try:
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            current_site = ''

        for form in formset:
            if form in formset.deleted_forms:
                continue

            first_name = form.cleaned_data.get('first_name')

            email = form.cleaned_data.get('email')
            tenant_id = self.request.user.tenant_id
            hash = sha256('%s-%s-%s-%s' % (
                tenant_id,
                email,
                date_string,
                settings.SECRET_KEY
            )).hexdigest()
            invite_link = '%s://%s%s' % (protocol, current_site, reverse_lazy('invitation_accept', kwargs={
                'tenant_id': tenant_id,
                'first_name': first_name,
                'email': email,
                'date': date_string,
                'hash': hash,
            }))

            # Email to the user
            send_templated_mail(
                template_name='invitation',
                recipient_list=[form.cleaned_data['email']],
                context={
                    'current_site': current_site,
                    'full_name': self.request.user.full_name,
                    'name': first_name,
                    'invite_link': invite_link,
                },
                from_email=settings.EMAIL_PERSONAL_HOST_USER,
                auth_user=settings.EMAIL_PERSONAL_HOST_USER,
                auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
            )

            post_intercom_event(event_name='invite-sent', user_id=self.request.user.id)

        if is_ajax(self.request):
            return HttpResponse(anyjson.serialize({
                'error': False,
                'html': _('The invitations were sent successfully'),
            }), content_type='application/json')
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        """
        This function is called when the formset didn't pass validation.
        If the request is done via ajax, send back a json object with the error set to true and
        the form rendered into a string.
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(formset=formset))
            return HttpResponse(anyjson.serialize({
                'error': True,
                'html': render_to_string(self.form_template_name, context)
            }), content_type='application/json')
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_success_url(self):
        """
        return the success url and set a succes message.
        """
        messages.success(self.request, _('I did it! I\'ve sent the invitations successfully.'))
        return '/#/preferences/company/users'


class AcceptInvitationView(FormView):
    """
    This is the view that handles the invitation link and registers the new user if everything
    goes according to plan, otherwise redirect the user to a failure template.
    """
    template_name = 'users/invitation/accept.html'
    template_failure = 'users/invitation/accept_invalid.html'
    form_class = UserRegistrationForm
    valid_link = False

    def dispatch(self, request, *args, **kwargs):
        """
        Set the variables needed and call super.
        This method tries to call dispatch to the right method.
        """
        self.first_name = kwargs.get('first_name')
        self.email = kwargs.get('email')
        self.datestring = kwargs.get('date')
        self.tenant_id = kwargs.get('tenant_id')
        self.hash = kwargs.get('hash')

        return super(AcceptInvitationView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """
        This method checks if the link is deemed valid, serves appropriate templates.
        """
        if not self.valid_link:
            return [self.template_failure]
        return super(AcceptInvitationView, self).get_template_names()

    def get(self, request, *args, **kwargs):
        """
        This function is called on normal page load. The function link_is_valid is called to
        determine whether the link is valid. If so load all the necessary data for the form etc.
        otherwise render the failure template (which get_template_names will return since link is
        invalid.
        """
        if self.link_is_valid():
            self.initial = {
                'first_name': self.first_name,
                'email': self.email,
            }
            return super(AcceptInvitationView, self).get(request, *args, **kwargs)

        messages.error(self.request, _('This invitation link is invalid or expired'))
        return HttpResponseRedirect(reverse_lazy('login'))

    def post(self, request, *args, **kwargs):
        """
        The function link_is_valid is called to determine if the link is valid.

        If so load all the necessary data for the form etc.
        otherwise render the failure template (which get_template_names will
        return since link is invalid).
        """
        if self.link_is_valid():
            self.initial = {
                'first_name': self.first_name,
                'email': self.email,
            }
            return super(AcceptInvitationView, self).post(request, *args, **kwargs)

        return self.render_to_response(self.get_context_data())

    def link_is_valid(self):
        """
        This functions performs all checks to verify the url is correct.

        Returns:
            Boolean: True if link is valid
        """
        # Default value is false, only set to true if all checks have passed
        self.valid_link = False

        if LilyUser.objects.filter(email__iexact=self.email).exists():
            return self.valid_link

        if not self.hash == sha256('%s-%s-%s-%s' % (
                self.tenant_id,
                self.email,
                self.datestring,
                settings.SECRET_KEY
        )).hexdigest():
            # hash should be correct
            return self.valid_link

        if not len(self.datestring) == 8:
            # Date should always be a string with a length of 8 characters
            return self.valid_link
        else:
            today = date.today()
            try:
                # Check if it is a valid date
                dateobj = date(int(self.datestring[4:8]), int(self.datestring[2:4]), int(self.datestring[:2]))
            except ValueError:
                return self.valid_link
            else:
                if (today < dateobj) or ((today - timedelta(days=settings.USER_INVITATION_TIMEOUT_DAYS)) > dateobj):
                    # Check if the link is not too old and not in the future
                    return self.valid_link

        # Every check was passed successfully, link is valid
        self.valid_link = True
        return self.valid_link

    def form_valid(self, form):
        """
        Create LilyUser.
        """
        user = LilyUser()
        user.email = self.email
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.set_password(form.cleaned_data['password'])
        user.tenant_id = self.tenant_id
        user.save()

        return self.get_success_url()

    def get_success_url(self):
        messages.success(self.request, _('Welcome to Lily! You can now log in with the information you provided.'))
        return redirect(reverse_lazy('login'))
