from django.contrib.auth.views import login
from django.contrib.auth import authenticate, login as user_login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.views.generic import View, TemplateView, FormView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import ugettext as _

from lily.utils.models import EmailAddressModel
from lily.contacts.models import ContactModel
from lily.users.models import UserModel
from lily.users.forms import CustomAuthenticationForm, RegistrationForm

class RegistrationView(FormView):
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
                
        # Generate activation link
        # uidb36 = int_to_base36(uid)
        
# TODO: support for Clients        user.client = form.cleaned_data['company']
# TODO: Activate user through activation links in emails 
        
        return self.get_success_url()
    
    def get_success_url(self):
        """
        Redirect to the success url.
        """
        
        return redirect(reverse_lazy('registration_success'))

class RegistrationSuccessView(TemplateView):
    template_name = 'users/registration_success.html'

class ActivationView(TemplateView):
    """
    This view checks whether the activation link is valid and acts accordingly.
    """
    # Template is only shown when something went wrong
    template_name = 'users/activation_failed.html'
    tgen = PasswordResetTokenGenerator()
    
    def get(self, request, *args, **kwargs):
        try:
            self.uid = base36_to_int(kwargs['uidb36'])
            self.user = UserModel.objects.get(id=self.uid)
            self.token = kwargs['token']
        except (ValueError, UserModel.DoesNotExist):
            # show template as per normal TemplateView behaviour
            return TemplateView.get(self, request, *args, **kwargs)
        
        if self.user.is_active:
            # redirect the user to login, since active == True and thus the link has already been used
            messages.info(request, _('Your account was already activated. You can log in here \
                                        and start browsing.'))
            return redirect(reverse_lazy('login'))
        elif self.tgen.check_token(self.user, self.token):
            # message that user is activated
            messages.success(request, _('Your account is now activated. You have been logged in \
                                        and can start browsing.'))
        else:
            # show template as per normal TemplateView behaviour
            return TemplateView.get(self, request, *args, **kwargs)
        
        # Set is_active to True and save the user
        self.user.is_active = True
        self.user.save()
        
        # log the user in
        self.user = authenticate(username=self.user.username, no_pass=True)
        user_login(request, self.user)
        
        # redirect to dashboard
        return redirect(reverse_lazy('dashboard'))
    
class ActivationResendView(TemplateView):
    template_name = 'users/activation_resend.html'

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
    template_name = 'base.html'
    
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)