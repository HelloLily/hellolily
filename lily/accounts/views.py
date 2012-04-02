from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView, DeleteView
from lily.accounts.forms import AddAccountMinimalForm, AddAccountForm, \
    EmailAddressBaseForm, EmailAddressBaseFormSet, AddressBaseForm, \
    AddressBaseFormSet, PhoneNumberBaseForm, PhoneNumberBaseFormSet, EditAccountForm
from lily.accounts.models import AccountModel
from lily.utils.models import SocialMediaModel


class AddAccountXHRView(CreateView):
    """
    View to add an account with only the minimum of fields included in the template.
    """
    
    template_name = 'accounts/account_add_xhr.html'
    form_template_name = 'accounts/account_add_xhr_form.html'
    form_class = AddAccountMinimalForm
    
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to check if the form is posted via ajax.
        """
        self.is_ajax = request.is_ajax()
        
        return super(AddAccountXHRView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Add e-mail to newly created account.
        """
        
        url = super(AddAccountXHRView,self).form_valid(form)
        
        form_kwargs = self.get_form_kwargs()
        account_instance = form_kwargs.get('instance')
        account_instance.email = form.cleaned_data.get('email')
        account_instance.save() 
        
        if self.is_ajax:
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': _('Account %s has been saved.') % account_instance.name
            }))
        
        return url
    
    def form_invalid(self, form):
        """
        Overloading super().form_invalid to return a different response to ajax requests.
        """
        
        if self.is_ajax:
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                 'error': True,
                 'html': render_to_string(self.form_template_name, context_instance=context)
            }), mimetype='application/javascript')
        
        return super(AddAccountXHRView, self).form_invalid(form)
    
    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted. This url
        can change depending on which button in the form was pressed.
        """
        # TODO: Return url based on pressed submit button
        return redirect(reverse('account_add_xhr'))


class AddAccountView(CreateView):
    """
    View to add an acccount with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    
    template_name = 'accounts/account_add.html'
    form_class = AddAccountForm
    
    # Create formsets
    EmailAddressFormSet = formset_factory(EmailAddressBaseForm, formset=EmailAddressBaseFormSet)
    AddressFormSet = formset_factory(AddressBaseForm, AddressBaseFormSet)
    PhoneNumberFormSet = formset_factory(PhoneNumberBaseForm, formset=PhoneNumberBaseFormSet)
    
    def get_form_kwargs(self):
        """
        Overloading super().get_form_kwargs() to add the user object to the keyword arguments for 
        instanciating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
            
        kwargs.update({
            'user': self.request.user
        })
        return kwargs
    
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to pass POST data to all custom formsets.
        """
        self.email_addresses_formset = self.EmailAddressFormSet(request.POST or None, prefix='email_addresses')
        self.addresses_formset = self.AddressFormSet(request.POST or None, prefix='addresses')
        self.phone_numbers_formset = self.PhoneNumberFormSet(request.POST or None, prefix='phone_numbers')

        return super(AddAccountView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Add m2m relations to newly created account (i.e. Social media, Phone numbers, 
        E-mail addresses and Addresses). 
        """
        
        cleaned_data = super(AddAccountView, self).form_valid(form)
        
        # Retrieve account instance to use
        form_kwargs = self.get_form_kwargs()
        account_instance = form_kwargs.get('instance')
        
        # Save all e-mail address, phone number and address formsets
        if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
            # Handle e-mail addresses
            for formset in self.email_addresses_formset:
                primary = form_kwargs.get('data').get('primary-email')
                if formset.prefix == primary:
                    formset.instance.is_primary = True
                
                # Only save e-mail address if something else than primary/status was filled in
                if formset.instance.email_address:
                    formset.save()
                    account_instance.email_addresses.add(formset.instance)
            
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
                    account_instance.addresses.add(formset.instance)
            
            # Handle phone numbers
            for formset in self.phone_numbers_formset:
                # Only save address if something was filled other than type
                if formset.instance.raw_input:
                    formset.save()
                    account_instance.phone_numbers.add(formset.instance)
        
        # Add relation to Facebook
        if cleaned_data.get('facebook'):
            facebook = SocialMediaModel.objects.create(
                name='facebook', 
                username=cleaned_data.get('facebook'),
                profile_url='http://www.facebook.com/%s' % cleaned_data.get('facebook'))
            account_instance.social_media.add(facebook)
        
        # Add relation to Twitter
        if cleaned_data.get('twitter'):
            twitter = SocialMediaModel.objects.create(
                name='twitter', 
                username=cleaned_data.get('twitter'),
                profile_url='http://twitter.com/%s' % cleaned_data.get('twitter'))
            account_instance.social_media.add(twitter)
        
        # Add relation to LinkedIn
        if cleaned_data.get('linkedin'):
            linkedin = SocialMediaModel.objects.create(
                name='linkedin',
                profile_url=cleaned_data.get('linkedin'))
            account_instance.social_media.add(linkedin)
        
        return self.get_success_url()
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
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
        return redirect(reverse('account_add'))
    

class EditAccountView(UpdateView):
    """
    View to edit an acccount with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    
    template_name = 'accounts/account_edit.html'
    form_class = EditAccountForm
    model = AccountModel
    
    # Create formsets
    EmailAddressFormSet = formset_factory(EmailAddressBaseForm, formset=EmailAddressBaseFormSet)
    AddressFormSet = formset_factory(AddressBaseForm, AddressBaseFormSet)
    PhoneNumberFormSet = formset_factory(PhoneNumberBaseForm, formset=PhoneNumberBaseFormSet)
    
    def get_form_kwargs(self):
        """
        Overloading super().get_form_kwargs() to add the user object to the keyword arguments for 
        instanciating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
            
        kwargs.update({
            'user': self.request.user
        })
        return kwargs
    
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to pass POST data to all custom formsets.
        """
        self.email_addresses_formset = self.EmailAddressFormSet(request.POST or None, prefix='email_addresses')
        self.addresses_formset = self.AddressFormSet(request.POST or None, prefix='addresses')
        self.phone_numbers_formset = self.PhoneNumberFormSet(request.POST or None, prefix='phone_numbers')

        return super(EditAccountView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Add m2m relations to newly created account (i.e. Social media, Phone numbers, 
        E-mail addresses and Addresses). 
        """
        
        cleaned_data = super(EditAccountView, self).form_valid(form)
        
        # Retrieve account instance to use
        form_kwargs = self.get_form_kwargs()
        account_instance = form_kwargs.get('instance')
        
        # Save all e-mail address, phone number and address formsets
        if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
            # Handle e-mail addresses
            for formset in self.email_addresses_formset:
                primary = form_kwargs.get('data').get('primary-email')
                if formset.prefix == primary:
                    formset.instance.is_primary = True
                
                # Only save e-mail address if something else than primary/status was filled in
                if formset.instance.email_address:
                    formset.save()
                    account_instance.email_addresses.add(formset.instance)
            
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
                    account_instance.addresses.add(formset.instance)
            
            # Handle phone numbers
            for formset in self.phone_numbers_formset:
                # Only save address if something was filled other than type
                if formset.instance.raw_input:
                    formset.save()
                    account_instance.phone_numbers.add(formset.instance)
        
        # Add relation to Facebook
        if cleaned_data.get('facebook'):
            facebook = SocialMediaModel.objects.create(
                name='facebook', 
                username=cleaned_data.get('facebook'),
                profile_url='http://www.facebook.com/%s' % cleaned_data.get('facebook'))
            account_instance.social_media.add(facebook)
        
        # Add relation to Twitter
        if cleaned_data.get('twitter'):
            twitter = SocialMediaModel.objects.create(
                name='twitter', 
                username=cleaned_data.get('twitter'),
                profile_url='http://twitter.com/%s' % cleaned_data.get('twitter'))
            account_instance.social_media.add(twitter)
        
        # Add relation to LinkedIn
        if cleaned_data.get('linkedin'):
            linkedin = SocialMediaModel.objects.create(
                name='linkedin',
                profile_url=cleaned_data.get('linkedin'))
            account_instance.social_media.add(linkedin)
        
        return self.get_success_url()
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs.update({
            'email_addresses_formset': self.email_addresses_formset,
            'addresses_formset': self.addresses_formset,
            'phone_numbers_formset': self.phone_numbers_formset,
        })
        return kwargs
    
    def get_object(self, queryset=None):
        obj = AccountModel.objects.get(pk=self.kwargs['pk'])
        return obj
    
    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted. 
        """
        return redirect(reverse('account_edit'))


class DeleteAccountView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    
    model = AccountModel
    
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to remove the instance if posted via ajax.
        """
        
        if request.is_ajax():
            self.remove()
        
        return super(DeleteAccountView, self).dispatch(request, *args, **kwargs)
    