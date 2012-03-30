# Django imports
from django.conf import settings
from django.contrib.auth.views import login
from django.contrib.auth import authenticate, login as user_login
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.views.generic import View, TemplateView, FormView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import ugettext as _

# 3rd party imports
from templated_email import send_templated_mail

# Lily imports
from lily.utils.models import EmailAddressModel
from lily.contacts.models import ContactModel
from lily.users.models import UserModel
from lily.users.forms import CustomAuthenticationForm, RegistrationForm, ResendActivationForm

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
        contact = ContactModel.objects.create(
            first_name=form.cleaned_data['first_name'],
            preposition=form.cleaned_data['preposition'],
            last_name=form.cleaned_data['last_name']
        )
        
        # Add email address
        email = EmailAddressModel.objects.create(
            email_address=form.cleaned_data['email'],
            is_primary=True
        )
        
        contact.email_addresses.add(email)
        
        # Create and save user
        user = UserModel()
        user.contact = contact
        user.username = form.cleaned_data['username']
        user.set_password(form.cleaned_data['password'])
        user.is_active = False
        user.save()
    
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
            from_email=settings.DEFAULT_FROM_EMAIL or 'no-reply@hellolily.com',
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
        
        return redirect(reverse_lazy('registration_success'))

class RegistrationSuccessView(TemplateView):
    """
    Show a success page after regstration.
    """
    template_name = 'users/registration_success.html'

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
            self.user = UserModel.objects.get(id=self.uid)
            self.token = kwargs['token']
        except (ValueError, UserModel.DoesNotExist):
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
        self.user = authenticate(username=self.user.username, no_pass=True)
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
        self.users = UserModel.objects.filter(
                                contact__email_addresses__email_address__iexact=form.cleaned_data['email'], 
                                contact__email_addresses__is_primary=True
                            )
        
        for user in self.users:
            # Get the current site or empty string
            try:
                self.current_site = Site.objects.get_current()
            except Site.DoesNotExist:
                self.current_site = ''
            
            # Generate uidb36 and token for the activation link
            self.uidb36 = int_to_base36(user.pk)
            self.token = self.TGen.make_token(user)
            
            # E-mail to the user
            send_templated_mail(
                template_name='activation',
                from_email=settings.DEFAULT_FROM_EMAIL or 'no-reply@hellolily.com',
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

class DashboardView(TemplateView):
    """
    This view shows the dashboard of the logged in user.
    """
    template_name = 'base.html'
    
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)