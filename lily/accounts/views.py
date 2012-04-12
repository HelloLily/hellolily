from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView, DeleteView
from lily.accounts.forms import AddAccountMinimalForm, AddAccountForm, EditAccountForm
from lily.accounts.models import AccountModel, TagModel
from lily.contacts.models import FunctionModel
from lily.utils.forms import EmailAddressBaseForm, AddressBaseForm, PhoneNumberBaseForm
from lily.utils.functions import is_ajax
from lily.utils.models import SocialMediaModel, EmailAddressModel, AddressModel, PhoneNumberModel


class AddAccountView(CreateView):
    """
    View to add an acccount with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets. Also supports a smaller
    form for ajax requests.
    """
    # Default template and form
    template_name = 'accounts/account_add.html'
    form_class = AddAccountForm

    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        if is_ajax(request):
            self.form_class = AddAccountMinimalForm
            self.template_name = 'accounts/account_add_xhr.html'
            self.form_template_name = 'accounts/account_add_xhr_form.html'
        else:
            self.EmailAddressFormSet = modelformset_factory(EmailAddressModel, form=EmailAddressBaseForm)
            self.AddressFormSet = modelformset_factory(AddressModel, form=AddressBaseForm)
            self.PhoneNumberFormSet = modelformset_factory(PhoneNumberModel, form=PhoneNumberBaseForm)
        
        return super(AddAccountView, self).dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """
        Overloading super().get_form_kwargs to add the user object to the keyword arguments for 
        instantiating the form.
        """
        kwargs = super(AddAccountView, self).get_form_kwargs()
        
        # Add the user object in the kwargs for the normal form
        if not is_ajax(self.request):
            kwargs.update({
                'user': self.request.user
            })
        return kwargs
    
    def get_form(self, form_class):
        """
        Overloading super().get_form to instantiate formsets while instantiating the form.
        """
        # Instantiate the formsets for the normal form
        if not is_ajax(self.request):
            self.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=EmailAddressModel.objects.none(), prefix='email_addresses')
            self.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=AddressModel.objects.none(), prefix='addresses')
            self.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=PhoneNumberModel.objects.none(), prefix='phone_numbers')
        
        return super(AddAccountView, self).get_form(form_class)
    
    def form_valid(self, form):
        """
        Add m2m relations to newly created account (i.e. Social media, Phone numbers, 
        E-mail addresses and Addresses). 
        """
        # Save instance
        super(AddAccountView, self).form_valid(form)
        
        form_kwargs = self.get_form_kwargs()
            
        if is_ajax(self.request):
            # Add e-mail address to account as primary
            self.object.email = form.cleaned_data.get('email')
            self.object.save()
            
            # Check if the user wants to 'add & edit'
            submit_action = form_kwargs['data'].get('submit', None)
            if submit_action == 'edit':
                do_redirect = True
                url = reverse('account_edit', kwargs={
                    'pk': self.object.pk,
                })
                html_response = ''
            else:
                do_redirect = False    
                url = ''
                html_response = _('Account %s has been saved.') % self.object.name
            
            # Return response 
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': html_response,
                'redirect': do_redirect,
                'url': url
            }))
        else: # Deal with all the extra fields on the normal form which are not in the ajax request
            # Save all e-mail address, phone number and address formsets
            if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
                # Handle e-mail addresses
                for formset in self.email_addresses_formset:
                    primary = form_kwargs['data'].get(formset.prefix + 'primary-email')
                    if formset.prefix == primary:
                        formset.instance.is_primary = True
                    
                    # Only save e-mail address if something else than primary/status was filled in
                    if formset.instance.email_address:
                        formset.save()
                        self.object.email_addresses.add(formset.instance)
                
                # Handle addresses
                for formset in self.addresses_formset:
                    # Only save address if something else than complement and/or type is filled in
                    if any([formset.instance.street,
                            formset.instance.street_number,
                            formset.instance.postal_code,
                            formset.instance.city,
                            formset.instance.state_province,
                            formset.instance.country]):
                        formset.save()
                        self.object.addresses.add(formset.instance)
                
                # Handle phone numbers
                for formset in self.phone_numbers_formset:
                    # Only save address if something was filled other than type
                    if formset.instance.raw_input:
                        formset.save()
                        self.object.phone_numbers.add(formset.instance)
            
            # Add relation to Facebook
            if form_kwargs['data'].get('facebook'):
                facebook = SocialMediaModel.objects.create(
                    name='facebook', 
                    username=form_kwargs['data'].get('facebook'),
                    profile_url='http://www.facebook.com/%s' % form_kwargs['data'].get('facebook'))
                self.object.social_media.add(facebook)
            
            # Add relation to Twitter
            if form_kwargs['data'].get('twitter'):
                twitter = SocialMediaModel.objects.create(
                    name='twitter', 
                    username=form_kwargs['data'].get('twitter'),
                    profile_url='http://twitter.com/%s' % form_kwargs['data'].get('twitter'))
                self.object.social_media.add(twitter)
            
            # Add relation to LinkedIn
            if form_kwargs['data'].get('linkedin'):
                linkedin = SocialMediaModel.objects.create(
                    name='linkedin',
                    profile_url=form_kwargs['data'].get('linkedin'))
                self.object.social_media.add(linkedin)
        
        return self.get_success_url()
    
    def form_invalid(self, form):
        """
        Overloading super().form_invalid to return a different response to ajax requests.
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                 'error': True,
                 'html': render_to_string(self.form_template_name, context_instance=context)
            }), mimetype='application/javascript')
        
        return super(AddAccountView, self).form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs = super(AddAccountView, self).get_context_data(**kwargs)
        
        # Add formsets to context for the normal form
        if not is_ajax(self.request):
            kwargs.update({
                'email_addresses_formset': self.email_addresses_formset,
                'addresses_formset': self.addresses_formset,
                'phone_numbers_formset': self.phone_numbers_formset,
            })
        return kwargs
    
    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted. 
        """
        return redirect(reverse('account_list'))
    

class EditAccountView(UpdateView):
    """
    View to edit an acccount with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    template_name = 'accounts/account_edit.html'
    form_class = EditAccountForm
    model = AccountModel
    
    # Create formsets
    EmailAddressFormSet = modelformset_factory(EmailAddressModel, form=EmailAddressBaseForm, can_delete=True)
    AddressFormSet = modelformset_factory(AddressModel, form=AddressBaseForm, can_delete=True)
    PhoneNumberFormSet = modelformset_factory(PhoneNumberModel, form=PhoneNumberBaseForm, can_delete=True)
    
    def get_form_kwargs(self):
        """
        Overloading super().get_form_kwargs to add the user object to the keyword arguments for 
        instantiating the form.
        """
        kwargs = super(EditAccountView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs
    
    def get_form(self, form_class):
        """
        Overloading super().get_form to instantiate formsets while instantiating the form.
        """
        form = super(EditAccountView, self).get_form(form_class)
        
        self.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=self.object.email_addresses.all(), prefix='email_addresses')
        self.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=self.object.addresses.all(), prefix='addresses')
        self.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=self.object.phone_numbers.all(), prefix='phone_numbers')
        
        return form
    
    def form_valid(self, form):
        """
        Save m2m relations to edited account (i.e. Social media, Phone numbers, 
        E-mail addresses and Addresses). 
        """
        # Save instance
        super(EditAccountView, self).form_valid(form)
        
        # Retrieve account instance to use
        form_kwargs = self.get_form_kwargs()
        
        # Save all e-mail address, phone number and address formsets
        if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
            # Handle e-mail addresses
            for formset in self.email_addresses_formset:
                # Check if existing instance has been marked for deletion
                if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                    self.object.email_addresses.remove(formset.instance)
                    formset.instance.delete()
                    continue
                
                # Check for e-mail address selected as primary
                primary = form_kwargs['data'].get(formset.prefix + 'primary-email')
                if formset.prefix == primary:
                    formset.instance.is_primary = True
                else:
                    formset.instance.is_primary = False
                
                # Only save e-mail address if something else than primary/status was filled in
                if formset.instance.email_address:
                    formset.save()
                    self.object.email_addresses.add(formset.instance)
            
            # Handle addresses
            for formset in self.addresses_formset:
                # Check if existing instance has been marked for deletion
                if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                    self.object.addresses.remove(formset.instance)
                    formset.instance.delete()
                    continue
                
                # Only save address if something else than complement and/or type is filled in
                if any([formset.instance.street,
                        formset.instance.street_number,
                        formset.instance.postal_code,
                        formset.instance.city,
                        formset.instance.state_province,
                        formset.instance.country]):
                    formset.save()
                    self.object.addresses.add(formset.instance)
            
            # Handle phone numbers
            for formset in self.phone_numbers_formset:
                # Check if existing instance has been marked for deletion
                if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                    self.object.phone_numbers.remove(formset.instance)
                    formset.instance.delete()
                    continue
                
                # Only save address if something was filled other than type
                if formset.instance.raw_input:
                    formset.save()
                    self.object.phone_numbers.add(formset.instance)
        
        # Add relation to Facebook
        if form_kwargs['data'].get('facebook'):
            facebook = SocialMediaModel.objects.create(
                name='facebook', 
                username=form_kwargs['data'].get('facebook'),
                profile_url='http://www.facebook.com/%s' % form_kwargs['data'].get('facebook'))
            self.object.social_media.add(facebook)
        
        # Add relation to Twitter
        if form_kwargs['data'].get('twitter'):
            twitter = SocialMediaModel.objects.create(
                name='twitter', 
                username=form_kwargs['data'].get('twitter'),
                profile_url='http://twitter.com/%s' % form_kwargs['data'].get('twitter'))
            self.object.social_media.add(twitter)
        
        # Add relation to LinkedIn
        if form_kwargs['data'].get('linkedin'):
            linkedin = SocialMediaModel.objects.create(
                name='linkedin',
                profile_url=form_kwargs['data'].get('linkedin'))
            self.object.social_media.add(linkedin)
        
        return self.get_success_url()
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs = super(EditAccountView, self).get_context_data(**kwargs)
        kwargs.update({
            'email_addresses_formset': self.email_addresses_formset,
            'addresses_formset': self.addresses_formset,
            'phone_numbers_formset': self.phone_numbers_formset,
        })
        return kwargs
    
    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted. 
        """
        # TODO: determine whether to go back to the list in search mode
        return redirect(reverse('account_list'))
#        return redirect(reverse('account_edit', kwargs={
#            'pk': self.object.pk,
#        }))


class DeleteAccountView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = AccountModel
    
    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        self.object = self.get_object()
        self.object.email_addresses.remove()
        self.object.addresses.remove()
        self.object.phone_numbers.remove()
        
        functions = FunctionModel.objects.filter(account=self.object)
        functions.delete()
        tags = TagModel.objects.filter(account=self.object)
        tags.delete()
        
        self.object.delete()
        
        # TODO: check for contacts ..
        
        return redirect(reverse('account_list'))

