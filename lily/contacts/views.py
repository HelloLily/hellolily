from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from lily.accounts.forms import EmailAddressBaseForm, AddressBaseForm, PhoneNumberBaseForm
from lily.contacts.forms import AddContactForm, EditContactForm
from lily.contacts.models import ContactModel
from lily.utils.models import EmailAddressModel, AddressModel, PhoneNumberModel

class AddContactView(CreateView):
    """
    View to add a contact with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    
    template_name = 'contacts/contact_add.html'
    form_class = AddContactForm
    
    # Create formsets
    EmailAddressFormSet = modelformset_factory(EmailAddressModel, form=EmailAddressBaseForm)
    AddressFormSet = modelformset_factory(AddressModel, form=AddressBaseForm)
    PhoneNumberFormSet = modelformset_factory(PhoneNumberModel, form=PhoneNumberBaseForm)
    
    def get_form(self, form_class):
        """
        Overloading super().get_form to instanciate formsets while instanciating the form.
        """
        form = super(AddContactView, self).get_form(form_class)
        
        self.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=EmailAddressModel.objects.none(), prefix='email_addresses')
        self.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=AddressModel.objects.none(), prefix='addresses')
        self.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=PhoneNumberModel.objects.none(), prefix='phone_numbers')
        
        return form
    
    def form_valid(self, form):
        """
        Add m2m relations to newly created contact (i.e. Phone numbers, E-mail addresses 
        and Addresses). 
        """
        
        # Save form
        super(AddContactView,self).form_valid(form)
        
        form_kwargs = self.get_form_kwargs()
        
        # Save all e-mail address, phone number and address formsets
        if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
            # Handle e-mail addresses
            for formset in self.email_addresses_formset:
                primary = form_kwargs['data'].get('primary-email')
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
        
        return self.get_success_url()
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs = super(AddContactView, self).get_context_data(**kwargs)
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
        return redirect(reverse('contact_add'))


class EditContactView(UpdateView):
    """
    View to edit a contact with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    
    template_name = 'contacts/contact_edit.html'
    form_class = EditContactForm
    model = ContactModel
    
    # Create formsets
    EmailAddressFormSet = modelformset_factory(EmailAddressModel, form=EmailAddressBaseForm, can_delete=True)
    AddressFormSet = modelformset_factory(AddressModel, form=AddressBaseForm, can_delete=True)
    PhoneNumberFormSet = modelformset_factory(PhoneNumberModel, form=PhoneNumberBaseForm, can_delete=True)
    
    def get_form(self, form_class):
        """
        Overloading super().get_form to instanciate formsets while instanciating the form.
        """
        form = super(EditContactView, self).get_form(form_class)
        
        self.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=self.object.email_addresses.all(), prefix='email_addresses')
        self.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=self.object.addresses.all(), prefix='addresses')
        self.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=self.object.phone_numbers.all(), prefix='phone_numbers')
        
        return form
    
    def form_valid(self, form):
        """
        Save m2m relations to edited contact (i.e. Phone numbers, E-mail addresses and Addresses). 
        """
        
        form_kwargs = self.get_form_kwargs()
        
        # Save all e-mail address, phone number and address formsets
        if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
            # Save form
            super(EditContactView, self).form_valid(form)
            
            # Handle e-mail addresses
            for formset in self.email_addresses_formset:
                # Check if existing instance has been marked for deletion
                if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                    self.object.email_addresses.remove(formset.instance)
                    formset.instance.delete()
                    continue
                
                # Check for e-mail address selected as primary
                primary = form_kwargs['data'].get('primary-email')
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
        
        return self.get_success_url()
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs = super(EditContactView, self).get_context_data(**kwargs)
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
        return redirect(reverse('contact_edit', kwargs={
            'pk': self.object.pk,
        }))

class DeleteContactView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    
    model = ContactModel
    
    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        
        self.object = self.get_object()
        self.object.email_addresses.remove()
        self.object.addresses.remove()
        self.object.phone_numbers.remove()
        self.object.delete()
        
        # TODO: check for functions ..
        
        return redirect(reverse('contact_list'))