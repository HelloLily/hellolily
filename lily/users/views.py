from datetime import date, timedelta
from hashlib import sha256
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as user_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import login
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import simplejson
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import ugettext as _
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View, TemplateView, FormView
from extra_views import FormSetView
from templated_email import send_templated_mail

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.users.decorators import group_required
from lily.users.forms import CustomAuthenticationForm, RegistrationForm, ResendActivationForm, \
    InvitationForm, InvitationFormset, UserRegistrationForm
from lily.users.models import CustomUser
from lily.utils.functions import is_ajax
from lily.utils.models import EmailAddress


class RegistrationView(FormView):
    """
    This view shows and handles the registration form, when valid register a new user.
    """
    template_name = 'users/registration.html'
    form_class = RegistrationForm
    
    def form_valid(self, form):
        """
        Register a new user.
        """
        # Create contact
        contact = Contact.objects.create(
            first_name=form.cleaned_data['first_name'],
            preposition=form.cleaned_data['preposition'],
            last_name=form.cleaned_data['last_name']
        )
        # Create account
        account = Account.objects.create(name=form.cleaned_data.get('company'))
        
        # Create and save user
        user = CustomUser()
        user.contact = contact
        user.account = account
        user.email = form.cleaned_data['email']
        
        # Store random unique data in username
        user.username = uuid4().get_hex()[:10]
        user.set_password(form.cleaned_data['password'])
        
        # Set inactive by default, activaten by e-mail required
        user.is_active = False
        user.save()
        
        # Add to admin group
        group, created = Group.objects.get_or_create(name='account_admin')
        user.groups.add(group)
    
        # Get the current site
        try:
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            current_site = ''
        
        # Generate uidb36 and token for the activation link
        uidb36 = int_to_base36(user.pk)
        tgen = PasswordResetTokenGenerator()
        token = tgen.make_token(user)
    
        # Send an activation mail
        # TODO: only create/save contact when e-mail sent succesfully
        send_templated_mail(
            template_name='activation',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[form.cleaned_data['email']],
            context={
                'current_site': current_site,
                'protocol': self.request.is_secure() and 'https' or 'http',
                'user': user,
                'uidb36': uidb36,
                'token': token,
            }
        )
                
# TODO: support for Clients        user.client = form.cleaned_data['company']
        
        return self.get_success_url()
    
    def get_success_url(self):
        """
        Redirect to the success url.
        """
        # TODO use messages to display registration succeeded
        return redirect(reverse_lazy('login'))


class ActivationView(TemplateView):
    """
    This view checks whether the activation link is valid and acts accordingly.
    """
    # Template is only shown when something went wrong
    template_name = 'users/activation_failed.html'
    tgen = PasswordResetTokenGenerator()
    
    def get(self, request, *args, **kwargs):
        """
        Check whether the activation link is valid, for this both the user id and the token should
        be valid. Messages are shown when user belonging to the user id is already active
        and when the account is succesfully activated. In all other cases the activation failed
        template is shown.
        Finally if the user is succesfully activated, log user in and redirect to their dashboard.
        """
        try:
            self.uid = base36_to_int(kwargs['uidb36'])
            self.user = CustomUser.objects.get(id=self.uid)
            self.token = kwargs['token']
        except (ValueError, CustomUser.DoesNotExist):
            # Show template as per normal TemplateView behaviour
            return TemplateView.get(self, request, *args, **kwargs)
        
        if self.tgen.check_token(self.user, self.token):
            # Message that user is activated
            messages.success(request, _('Your account is now activated. You have been logged in' \
                                        ' and can start browsing.'))
        else:
            # Show template as per normal TemplateView behaviour
            return TemplateView.get(self, request, *args, **kwargs)
        
        # Set is_active to True and save the user
        self.user.is_active = True
        self.user.save()
        
        # Log the user in
        self.user = authenticate(username=self.user.email, no_pass=True)
        user_login(request, self.user)
        
        # Redirect to dashboard
        return redirect(reverse_lazy('dashboard'))


class ActivationResendView(FormView):
    """
    This view is used by an user to request a new activation e-mail.
    """
    template_name = 'users/activation_resend.html'
    form_class = ResendActivationForm
    
    def form_valid(self, form):
        """
        If ResendActivationForm passed the validation, generate new token and send an e-mail.
        """
        self.TGen = PasswordResetTokenGenerator()
        self.users = CustomUser.objects.filter(
                                contact__email_addresses__email_address__iexact=form.cleaned_data['email'], 
                                contact__email_addresses__is_primary=True
                            )
        
        # Get the current site or empty string
        try:
            self.current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            self.current_site = ''
        
        for user in self.users:
            # Generate uidb36 and token for the activation link
            self.uidb36 = int_to_base36(user.pk)
            self.token = self.TGen.make_token(user)
            
            # E-mail to the user
            send_templated_mail(
                template_name='activation',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[form.cleaned_data['email']],
                context={
                    'current_site': self.current_site,
                    'protocol': self.request.is_secure() and 'https' or 'http',
                    'full_name': " ".join([user.contact.first_name, user.contact.preposition, user.contact.last_name]),
                    'user': user,
                    'uidb36': self.uidb36,
                    'token': self.token,
                }
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
    
    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user wants to be remembered and return the default login view.
        """
        if request.user.is_authenticated():
            return(redirect(reverse_lazy('dashboard')))
        
        if request.method == 'POST':
            # If not using 'remember me' feature use default expiration time.
            if not request.POST.get('remember_me', False):
                request.session.set_expiry(None)
        return login(request, template_name='users/login.html', authentication_form=CustomAuthenticationForm, *args, **kwargs)


class SendInvitationView(FormSetView):
    """
    This view is used to invite new people to the site. It works with a formset to allow easy
    adding of multiple invitations. It also checks whether the call is done via ajax or via a normal
    form, to use ajax append ?xhr to the url.
    """
    template_name = 'users/invitation_send.html'
    form_template_name = 'users/invitation_send_form.html'
    form_class = InvitationForm
    formset_class = InvitationFormset
    extra = 1
    
    def formset_valid(self, formset):
        """
        This function is called when the formset is deemed valid.
        An email is sent to all email fields which are filled in.
        If the request is done via ajax give json back with a success message, otherwise
        redirect to the success url.
        """
        self.protocol = self.request.is_secure() and 'https' or 'http'
        self.account = self.request.user.account
        self.b36accountpk = int_to_base36(self.account.pk)
        self.date = date.today().strftime('%d%m%Y')
        
        # Get the current site or empty string
        try:
            self.current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            self.current_site = ''
        
        for form in formset:
            first_name = form.cleaned_data.get('first_name')
            email = form.cleaned_data.get('email')
            if email: # check that the email is not empty
                self.hash = sha256('%s-%s-%s-%s' % (self.account.name, email, self.date, settings.SECRET_KEY)).hexdigest()
                self.invite_link = '%s://%s%s' % (self.protocol, self.current_site, reverse_lazy('invitation_accept', kwargs={
                    'account_name': self.account.name,
                    'first_name': first_name,
                    'email': email,
                    'date': self.date,
                    'aidb36': self.b36accountpk,
                    'hash': self.hash,
                }))
                
                # E-mail to the user
                send_templated_mail(
                    template_name='invitation',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[form.cleaned_data['email']],
                    context={
                        'current_site': self.current_site,
                        'full_name': self.request.user.contact.full_name(),
                        'name': first_name,
                        'invite_link': self.invite_link,
                        'company_name': self.account.name,
                    }
                )
        
        if is_ajax(self.request):
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': _('The invitations were sent successfully'),
            }))
        return HttpResponseRedirect(self.get_success_url())
    
    def formset_invalid(self, formset):
        """
        This function is called when the formset didn't pass validation.
        If the request is done via ajax, send back a json object with the error set to true and 
        the form rendered into a string.
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(formset=formset))
            return HttpResponse(simplejson.dumps({
                'error': True,
                'html': render_to_string(self.form_template_name, context)
            }), mimetype='application/javascript')
        return self.render_to_response(self.get_context_data(formset=formset))
    
    def get_success_url(self):
        """
        return the success url and set a succes message.
        """
        messages.success(self.request, _('The invitations were sent successfully.'))
        return reverse_lazy('dashboard')


class AcceptInvitationView(FormView):
    """
    This is the view that handles the invatation link and registers the new user if everything
    goes according to plan, otherwise redirect the user to a failure template.
    """
    template_name = "users/invitation_accept.html"
    template_failure = "users/invitation_failed.html"
    form_class = UserRegistrationForm
    valid_link = False
    
    def dispatch(self, request, *args, **kwargs):
        """
        Set the variables needed and call super.
        This method tries to call dispatch to the right method.
        """
        self.account_name = kwargs.get('account_name')
        self.first_name = kwargs.get('first_name')
        self.email = kwargs.get('email')
        self.datestring = kwargs.get('date')
        self.aidb36 = kwargs.get('aidb36')
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
        determine wheter the link is valid. If so load all the necesary data for the form etc.
        otherwise render the failure template (which get_template_names will return since link is 
        invalid.
        """
        if self.link_is_valid():
            self.initial = {
                'first_name': self.first_name,
                'email': self.email,
                'company': self.account_name,
            }
            return super(AcceptInvitationView, self).get(request, *args, **kwargs)
        
        self.object = None
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        This function is called on a form submit. The function link_is_valid is called to 
        determine wheter the link is valid. If so load all the necesary data for the form etc.
        otherwise render the failure template (which get_template_names will return since link is 
        invalid.
        """
        if self.link_is_valid():
            self.initial = {
                'first_name': self.first_name,
                'email': self.email,
                'company': self.account_name,
            }
            return super(AcceptInvitationView, self).post(request, *args, **kwargs)
        
        self.object = None
        return self.render_to_response(self.get_context_data())
    
    def link_is_valid(self):
        """
        This functions performs all checks to verify the url is correct.
        It returns the boolean value but also sets a class variable with this boolean.
        """
        # Default value is false, only set to true if all checks have passed
        self.valid_link = False
            
        if CustomUser.objects.filter(contact__email_addresses__email_address__iexact=self.email).exists():
            return self.valid_link
        
        try:
            # Check if it's a valid pk and try to retrieve the corresponding account
            self.account = Account.objects.get(pk=base36_to_int(self.aidb36))
        except ValueError, Account.DoesNotExist:
            return self.valid_link
        else:
            if not self.account.name == self.account_name:
                # The account name from url should be same as in database
                return self.valid_link
            elif not self.hash == sha256('%s-%s-%s-%s' % (self.account.name, self.email, self.datestring, settings.SECRET_KEY)).hexdigest():
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
        
        self.valid_link = True
        return self.valid_link
    
    def form_valid(self, form):
        """
        This function is called when the form is deemed valid. The new user is created and the
        get_success_url method is called.
        """
        try:
            contact = Contact.objects.get(email_addresses__email_address=self.email, email_addresses__is_primary=True)
        except Contact.DoesNotExist:
            contact = Contact.objects.create(
                first_name=form.cleaned_data['first_name'],
                preposition=form.cleaned_data['preposition'],
                last_name=form.cleaned_data['last_name']
            )
            email = EmailAddress.objects.create(
                email_address=form.cleaned_data['email'],
                is_primary=True
            )
            contact.email_addresses.add(email)
        
        # Create and save user
        user = CustomUser()
        user.contact = contact
        user.account = self.account
        user.username = uuid4().get_hex()[:10]
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        return self.get_success_url()
    
    def get_success_url(self):
        """
        Redirect to the success page.
        """
        return redirect(reverse_lazy('login'))


class DashboardView(TemplateView):
    """
    This view shows the dashboard of the logged in user.
    """
    template_name = 'users/dashboard.html'

# Perform logic here instead of in urls.py
registration_view = RegistrationView.as_view()
activation_view = ActivationView.as_view()
activation_resend_view = ActivationResendView.as_view()
login_view = LoginView.as_view()
send_invitation_view = group_required('account_admin')(SendInvitationView.as_view())
dashboard_view = login_required(DashboardView.as_view())