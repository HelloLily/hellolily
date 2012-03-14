from django.contrib.auth.views import login
from django.views.generic import View, TemplateView, FormView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect

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

class LoginView(View):
    """
    This view extends the default login view with a 'remember me' feature.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user wants to be remembered and return the default login view.
        """
                
        if request.method == 'POST':
            # If not using 'remember me' feature use default expiration time.
            if not request.POST.get('remember_me', False):
                request.session.set_expiry(None)
        return login(request, template_name='users/login.html', authentication_form=CustomAuthenticationForm, *args, **kwargs)

class DashboardView(TemplateView):    
    template_name = 'base.html'
    
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)