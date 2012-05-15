from datetime import date, timedelta
from hashlib import sha256
import base64
import pickle

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.forms.models import modelformset_factory, inlineformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.html import escapejs
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from templated_email import send_templated_mail

from lily.accounts.models import Account
from lily.contacts.forms import AddContactForm, AddContactMinimalForm, EditContactForm, \
    FunctionForm, EditFunctionForm
from lily.contacts.models import Contact, Function
from lily.users.models import CustomUser
from lily.utils.forms import EmailAddressBaseForm, AddressBaseForm, PhoneNumberBaseForm, NoteForm
from lily.utils.functions import is_ajax, clear_messages
from lily.utils.models import SocialMedia, EmailAddress, Address, PhoneNumber
from lily.utils.templatetags.messages import tag_mapping
from lily.utils.views import DetailFormView


class ListContactView(ListView):
    """
    Display a list of all contacts
    """
    template_name = 'contacts/contact_list.html'
    model = Contact
    
    def get_queryset(self):
        """
        Overriding super().get_queryset to limit the queryset based on a kwarg when provided.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            # If kwarg is provided, try reducing the queryset
            if self.kwargs.get('b36_pks', None):
                try:
                    # Convert base36 to int
                    b36_pks = self.kwargs.get('b36_pks').split(';')
                    int_pks = []
                    for pk in b36_pks:
                        int_pks.append(base36_to_int(pk))
                    # Filter queryset
                    queryset = self.model._default_manager.filter(pk__in=int_pks)
                except:
                    queryset = self.model._default_manager.all()
            else:
                queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset


class DetailContactView(DetailFormView):
    """
    Display a detail page for one contact.
    """
    template_name = 'contacts/contact_details.html'
    model = Contact
    form_class = NoteForm
    
    def form_valid(self, form):
        note = form.save(commit=False)
        note.author = self.request.user
        note.subject = self.object
        note.save()
        
        return super(DetailContactView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('contact_details', kwargs={'pk': self.object.pk})


class AddContactView(CreateView):
    """
    View to add a contact with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    
    # Default template and form
    template_name = 'contacts/contact_add.html'
    form_class = AddContactForm
    
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        if is_ajax(request):
            self.form_class = AddContactMinimalForm
            self.template_name = 'contacts/contact_add_xhr_form.html'
        else:
            self.EmailAddressFormSet = modelformset_factory(EmailAddress, form=EmailAddressBaseForm, extra=0)
            self.AddressFormSet = modelformset_factory(Address, form=AddressBaseForm, extra=0)
            self.PhoneNumberFormSet = modelformset_factory(PhoneNumber, form=PhoneNumberBaseForm, extra=0)
        
        return super(AddContactView, self).dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class):
        """
        Overloading super().get_form to instantiate formsets while instantiating the form.
        """
        form = super(AddContactView, self).get_form(form_class)
        
        # Instantiate the formsets for the normal form
        if not is_ajax(self.request):
            self.email_addresses_formset = form.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=EmailAddress.objects.none(), prefix='email_addresses')
            self.addresses_formset = form.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=Address.objects.none(), prefix='addresses')
            self.phone_numbers_formset = form.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=PhoneNumber.objects.none(), prefix='phone_numbers')
        
        return form
    
    def form_valid(self, form):
        """
        Add m2m relations to newly created contact (i.e. Phone numbers, E-mail addresses 
        and Addresses). 
        """
        # Save instance
        super(AddContactView, self).form_valid(form)
        
        # Retrieve contact instance to use
        form_kwargs = self.get_form_kwargs()
        
        if is_ajax(self.request):
            # Add e-mail address to account as primary
            self.object.primary_email = form.cleaned_data.get('email')
            self.object.save()
            
            # Save website
            if form.cleaned_data.get('phone'):
                phone = PhoneNumber.objects.create(raw_input=form.cleaned_data.get('phone'))
                self.object.phone_numbers.add(phone)
            
            # Check if the user wants to 'add & edit'
            submit_action = form_kwargs['data'].get('submit_button', None)
            if submit_action == 'edit':
                do_redirect = True
                url = reverse('contact_edit', kwargs={
                    'pk': self.object.pk,
                })
                notification = False
                html_response = ''
            else:
                list_url = reverse('contact_list')
                message = _('%s (Contact) has been saved.') % self.object.full_name()

                # Redirect if in the list view
                if self.request.META['HTTP_REFERER'].endswith(list_url):
                    # Show save message
                    messages.success(self.request, message)
            
                    do_redirect = True    
                    url = list_url
                    notification = False
                    html_response = ''
                else:
                    do_redirect = False    
                    url = ''
                    html_response = ''
                    notification = [{ 'message': escapejs(message), 'tags': tag_mapping.get('success') }]
            
            # Return response 
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': html_response,
                'redirect': do_redirect,
                'notification': notification,
                'url': url
            }), mimetype='application/json')
        else: # Deal with all the extra fields on the normal form which are not in the ajax request
            # Save all e-mail address, phone number and address formsets
            if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
                # Handle e-mail addresses
                for formset in self.email_addresses_formset:
                    primary = form_kwargs['data'].get(self.email_addresses_formset.prefix + '_primary-email')
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
    
            # Save any selected accounts
            if form_kwargs['data'].getlist('accounts'):
                pks = form_kwargs['data'].getlist('accounts')
                for pk in pks:
                    account = Account.objects.get(pk=pk)
                    Function.objects.create(account=account, contact=self.object, manager=self.object)
        
            # Show save message
            messages.success(self.request, _('%s (Contact) has been saved.') % self.object.full_name());
        
        # Save selected account
        if form_kwargs['data'].get('account'):
            pk = form_kwargs['data'].get('account')
            account = Account.objects.get(pk=pk)
            Function.objects.get_or_create(account=account, contact=self.object, manager=self.object)
            
        # Add relation to Facebook
        if form_kwargs['data'].get('facebook'):
            facebook = SocialMedia.objects.create(
                name='facebook', 
                username=form_kwargs['data'].get('facebook'),
                profile_url='http://www.facebook.com/%s' % form_kwargs['data'].get('facebook'))
            self.object.social_media.add(facebook)
        
        # Add relation to Twitter
        if form_kwargs['data'].get('twitter'):
            twitter = SocialMedia.objects.create(
                name='twitter', 
                username=form_kwargs['data'].get('twitter'),
                profile_url='http://twitter.com/%s' % form_kwargs['data'].get('twitter'))
            self.object.social_media.add(twitter)
        
        # Add relation to LinkedIn
        if form_kwargs['data'].get('linkedin'):
            linkedin = SocialMedia.objects.create(
                name='linkedin',
                profile_url=form_kwargs['data'].get('linkedin'))
            self.object.social_media.add(linkedin)
        
        return self.get_success_url()
    
    def form_invalid(self, form):
        """
        Overloading super().form_invalid to mark the primary checkbox for e-mail addresses as 
        checked for postbacks. 
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                'error': True,
                'html': render_to_string(self.template_name, context_instance=context)
            }), mimetype='application/json')
        else:
            # Check for the e-mail address to select as primary
            form_kwargs = self.get_form_kwargs()
            primary = form_kwargs['data'].get(self.email_addresses_formset.prefix + '_primary-email')
            
            for formset in self.email_addresses_formset:
                if formset.prefix == primary:
                    # Mark as selected
                    formset.instance.is_primary = True
                    # TODO: try making the field selected to prevent double if statements in templates
#                    formset.fields['is_primary'].widget.__dict__['attrs'].update({ 'checked': 'checked' })
        
        return super(AddContactView, self).form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs = super(AddContactView, self).get_context_data(**kwargs)
        
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
        return redirect(reverse('contact_list_filtered', kwargs={'b36_pks': int_to_base36(self.object.pk)}))


class EditContactView(UpdateView):
    """
    View to edit a contact with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    template_name = 'contacts/contact_edit.html'
    form_class = EditContactForm
    model = Contact
    
    # Create formsets
    EmailAddressFormSet = modelformset_factory(EmailAddress, form=EmailAddressBaseForm, can_delete=True, extra=0)
    AddressFormSet = modelformset_factory(Address, form=AddressBaseForm, can_delete=True, extra=0)
    PhoneNumberFormSet = modelformset_factory(PhoneNumber, form=PhoneNumberBaseForm, can_delete=True, extra=0)
    
    def get_form(self, form_class):
        """
        Overloading super().get_form to instantiate formsets while instantiating the form.
        """
        form = super(EditContactView, self).get_form(form_class)
        
        # Also link formsets to form to allow validation
        self.email_addresses_formset = form.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=self.object.email_addresses.all(), prefix='email_addresses')
        self.addresses_formset = form.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=self.object.addresses.all(), prefix='addresses')
        self.phone_numbers_formset = form.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=self.object.phone_numbers.all(), prefix='phone_numbers')
        
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
            allow_edit_email = email_verify = False
            # TODO: move the permission logic to a decorator for this view
            
            # Permission check: users in a certain group and the contact's user can edit e-mail adresses
            # For e-mailaddresses a confirmation e-mail is sent to the new e-mail adres when 
            # the contact's user changes it. Another user with permissions can change it regardless.
            try:
                user = CustomUser.objects.get(contact=self.object)
                
                # If it's the current logged in user's contact
                if user == self.request.user:
                    # Allow editing, but sent verification e-mails
                    allow_edit_email = email_verify = True
                else:
                    # If the the current logged in user has the right permissions
                    if 'account_admin' in self.request.user.groups.values_list('name', flat=True):
                        # Allow editing 
                        allow_edit_email = True                   
            except CustomUser.DoesNotExist:
                # If it's not a user's contact
                allow_edit_email = True
            
            if allow_edit_email:
                for formset in self.email_addresses_formset:
                    # Check for e-mail address selected as primary
                    primary = form_kwargs['data'].get(self.email_addresses_formset.prefix + '_primary-email')
                    
                    # Check if existing instance has been marked for deletion
                    if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                        self.object.email_addresses.remove(formset.instance)
                        # Don't delete if it's the one marked as primary
                        if formset.prefix != primary:
                            formset.instance.delete()
                        continue
                    
                    # Make sure only one is marked as primary
                    if formset.prefix == primary:
                        formset.instance.is_primary = True
                    else:
                        formset.instance.is_primary = False
                    
                    # Only save e-mail address if something else than primary/status was filled in
                    if formset.instance.email_address:
                        # Check if only the is_primary attribute has changed, if so allow the save.
                        allow_save = False
                        existing_email_address = None
                        if formset.instance.pk:
                            existing_email_address = EmailAddress.objects.get(pk=formset.instance.pk)
                            if existing_email_address.email_address == formset.instance.email_address:
                                allow_save = True
                        
                        if not email_verify or allow_save:
                            formset.save()
                            self.object.email_addresses.add(formset.instance)
                        else:
                            # get old/new e-mail address
                            old_email = self.request.user.contact.email_addresses.filter(pk=form.instance.pk).values_list('email_address', flat=True)[0]
                            new_email = formset.instance.email_address
                            # get contact pk
                            pk = self.object.pk
                            # calculate expire date
                            expire_date = date.today() + timedelta(days=settings.EMAIL_CONFIRM_TIMEOUT_DAYS)
                            expire_date_pickled = pickle.dumps(expire_date)
                            
                            # get link to site
                            protocol = self.request.is_secure() and 'https' or 'http'
                            site = Site.objects.get_current()
                            
                            # Build data dict
                            data = base64.urlsafe_b64encode(pickle.dumps({
                                'contact_pk': self.object.pk,
                                'old_email': old_email,
                                'email_address': pickle.dumps(formset.instance),
                                'expire_date': expire_date_pickled,
                                'hash': sha256('%s%s%d%s' % (old_email, new_email, pk, expire_date_pickled)).hexdigest(),
                            })).strip('=')
                            
                            # Build verification link
                            verification_link = "%s://%s%s" % (protocol, site, reverse('contact_confirm_email', kwargs={
                                'data': data
                            }))
                            
                            # Sent an e-mail to the user current primary adress
                            send_templated_mail(
                                template_name='email_confirm',
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[new_email],
                                context = {
                                    'current_site': site,
                                    'full_name': self.object.full_name(),
                                    'verification_link': verification_link,
                                    'email_address': formset.instance.email_address
                                }
                            )
                            
                            # Add message
                            messages.info(self.request, _('An e-mail was sent to %s with a link to verify a new e-mail address.' % formset.instance.email_address))
            
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
        
        # Save any selected accounts
#        if form_kwargs['data'].getlist('accounts'):
#            pks = form_kwargs['data'].getlist('accounts')
#            for pk in pks:
#                account = Account.objects.get(pk=pk)
#                Function.objects.get_or_create(account=account, contact=self.object, manager=self.object)
#            functions = Function.objects.filter(~Q(account_id__in=pks), Q(contact=self.object))
#            functions.delete()
#        else:
#            functions = Function.objects.filter(contact=self.object)
#            functions.delete()

        # Save selected account
        if form_kwargs['data'].get('account'):
            pk = form_kwargs['data'].get('account')
            account = Account.objects.get(pk=pk)
            Function.objects.get_or_create(account=account, contact=self.object, manager=self.object)
            
            functions = Function.objects.filter(~Q(account_id=pk), Q(contact=self.object))
            functions.delete()
        else:
            # No account selected
            functions = Function.objects.filter(contact=self.object)
            functions.delete()
            
        # Add relation to Facebook
        if form_kwargs['data'].get('facebook'):
            # Prevent re-creating
            facebook, created = SocialMedia.objects.get_or_create(
                name='facebook', 
                username=form_kwargs['data'].get('facebook'),
                profile_url='http://www.facebook.com/%s' % form_kwargs['data'].get('facebook'))
            if created:
                self.object.social_media.add(facebook)
        else:
            # Remove possible Facebook relations
            self.object.social_media.filter(name='facebook').delete()
        
        # Add relation to Twitter
        if form_kwargs['data'].get('twitter'):
            # Prevent re-creating
            twitter, created = SocialMedia.objects.get_or_create(
                name='twitter', 
                username=form_kwargs['data'].get('twitter'),
                profile_url='http://twitter.com/%s' % form_kwargs['data'].get('twitter'))
            if created:
                self.object.social_media.add(twitter)
        else:
            # Remove possible Twitter relations
            self.object.social_media.filter(name='twitter').delete()
        
        # Add relation to LinkedIn
        if form_kwargs['data'].get('linkedin'):
            # Prevent re-creating
            linkedin, created = SocialMedia.objects.get_or_create(
                name='linkedin',
                profile_url=form_kwargs['data'].get('linkedin'))
            if created:
                self.object.social_media.add(linkedin)
        else:
            # Remove possible LinkedIn relations
            self.object.social_media.filter(name='linkedin').delete()
        
        # Show save message
        messages.success(self.request, _('%s (Contact) has been edited.') % self.object.full_name());
        
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
#        form_kwargs = self.get_form_kwargs()
#        
#        if len(Function.objects.filter(contact=self.object)) > 0 and form_kwargs['data'].get('edit_accounts'):
#            return redirect(reverse('function_edit', kwargs={
#                'pk': self.object.pk,
#            }))
        
        return redirect(reverse('contact_list_filtered', kwargs={'b36_pks': int_to_base36(self.object.pk)}))


class DeleteContactView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Contact
    
    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        self.object = self.get_object()
        self.object.email_addresses.remove()
        self.object.addresses.remove()
        self.object.phone_numbers.remove()
        
        functions = Function.objects.filter(contact=self.object)
        functions.delete()
        
        # Show delete message
        messages.success(self.request, _('%s (Contact) has been deleted.') % self.object.full_name());
        
        self.object.delete()
        
        return redirect(reverse('contact_list'))


class EditFunctionView(UpdateView):
    """
    View to edit functions a contact has.
    """
    template_name = 'contacts/function_edit.html'
    form_class = EditFunctionForm
    model = Contact
    
    FunctionFormSet = inlineformset_factory(Contact, Function, fk_name='contact', form=FunctionForm, extra=0)
    EmailAddressFormSet = modelformset_factory(EmailAddress, form=EmailAddressBaseForm, can_delete=True, extra=0)
    PhoneNumberFormSet = modelformset_factory(PhoneNumber, form=PhoneNumberBaseForm, can_delete=True, extra=0)
    
    def get_form(self, form_class):
        """
        Overloading super().get_form to instantiate formsets while instantiating the form.
        """
        form = super(EditFunctionView, self).get_form(form_class)
        
        # Create function formset with all existing functions for current contact
        self.formset = form.formset = self.FunctionFormSet(self.request.POST or None, instance=self.object)
        
        # Add e-mail address and phone number formsets to each function form, each with a unique prefix
        for _form in self.formset.forms:
            _form.email_addresses_formset = self.EmailAddressFormSet(data=self.request.POST or None, queryset=_form.instance.email_addresses.all(), prefix='email_addresses_%s' % _form.instance.pk)
            _form.phone_numbers_formset = self.PhoneNumberFormSet(data=self.request.POST or None, queryset=_form.instance.phone_numbers.all(), prefix='phone_numbers_%s' % _form.instance.pk)
        
        return form
    
    def form_valid(self, form):
        """
        Overloading super.form_valid to save the forms in formset.
        """
        if self.formset.is_valid():
            for form in self.formset:
                # Save all e-mail address, phone number and address formsets
                if form.email_addresses_formset.is_valid() and form.phone_numbers_formset.is_valid():
                    
                    # Save form
                    form.save()
                    
                    form_kwargs = self.get_form_kwargs()
                    
                    # Handle e-mail addresses
                    for formset in form.email_addresses_formset:
                        # Check if existing instance has been marked for deletion
                        if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                            form.instance.email_addresses.remove(formset.instance)
                            formset.instance.delete()
                            continue
                        
                        # Check for e-mail address selected as primary
                        primary = form_kwargs['data'].get(form.email_addresses_formset.prefix + '_primary-email')
                        if formset.prefix == primary:
                            formset.instance.is_primary = True
                        else:
                            formset.instance.is_primary = False
                        
                        # Only save e-mail address if something else than primary/status was filled in
                        if formset.instance.email_address:
                            formset.save()
                            form.instance.email_addresses.add(formset.instance)
                    
                    # Handle phone numbers
                    for formset in form.phone_numbers_formset:
                        # Check if existing instance has been marked for deletion
                        if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                            form.instance.phone_numbers.remove(formset.instance)
                            formset.instance.delete()
                            continue
                        
                        # Only save address if something was filled other than type
                        if formset.instance.raw_input:
                            formset.save()
                            form.instance.phone_numbers.add(formset.instance)
        
        # Immediately return the success url, no need to save a non-edited Contact instance.
        return self.get_success_url()
    
    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formset to context.
        """
        kwargs = super(EditFunctionView, self).get_context_data(**kwargs)
        kwargs.update({
            'formset': self.formset,
        })
        return kwargs
    
    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted. 
        """
        return redirect(reverse('contact_list'))
    
    class Meta:
        fields = ()
    

class ConfirmContactEmailView(TemplateView):
    """
    Confirm an e-mail address change for a contact which is linked to a user. 
    """
    http_method_names = ['get']
    
    def get(self, request, *args, **kwargs):
        """
        Verify the incoming request uri. Save the new e-mail address or throw a 404.
        """
        # Base64 decode and unpickle data from URL
        try:
            data = pickle.loads(base64.urlsafe_b64decode(str(kwargs.get('data') + '=' * (len(kwargs.get('data')) % 4))))
        except:
            raise Http404
        if self.is_valid_link(data):
            # Unpickle EmailAddress object
            try:
                email_address = pickle.loads(data.get('email_address'))
            except:
                # throw 404
                raise Http404
                    
            # Get contact
            contact_pk = data.get('contact_pk')
            user = CustomUser.objects.get(pk=contact_pk)
            
            # Save e-mail address
            if email_address.pk is None and user.contact.email_addresses.filter(email_address=email_address.email_address).exists():
                # throw 404
                raise Http404
            else:
                # Prevent multiple primary e-mail addresses 
                if email_address.is_primary:
                    user.contact.email_addresses.all().update(is_primary=False)
                
                email_address.save()
                user.contact.email_addresses.add(email_address)
            
            # if logged in:
            if request.user.is_authenticated() and email_address.is_primary:
                # clear any existing messages
                clear_messages(request)
                # add message
                messages.success(request, _('Your primary e-mail address has been changed. Please log back in.'))
                
                # force log out
                return redirect(reverse('logout'))
            else:
                # redirect to contact edit/view page
                return redirect(reverse('contact_details', kwargs={
                    'pk': contact_pk
                 }))
        else:
            # throw 404
            raise Http404
        
    def is_valid_link(self, data):
        """
        Verify the kwargs from the uri with the data in the hash.
        """
        # grab hash
        hash = data.get('hash')
        # grab old/new e-mail address
        old_email = data.get('old_email')
        
        # Unpickle EmailAddress object 
        email_address = pickle.loads(data.get('email_address'))
        new_email = email_address.email_address
        # grab pk
        pk = data.get('contact_pk')
        # grab datetime to test expire date
        expire_date_pickled = data.get('expire_date')
        
        # Verify hash
        if hash != sha256('%s%s%d%s' % (old_email, new_email, pk, expire_date_pickled)).hexdigest():
            return False
        
        # Test expire date
        try:
            expire_date = pickle.loads(expire_date_pickled)
            if date.today() > expire_date:
                # Expire date has passed
                return False
        except pickle.UnpicklingError:
            return False
        
        # Find a user's contact with old_email as an existing e-mail address
        if old_email == '' and not force_unicode(old_email) in CustomUser.objects.filter(pk=pk).values_list('contact__email_addresses__email_address', flat=True):
            # No e-mail found to change
            return False
        
        return True


# Perform logic here instead of in urls.py
add_contact_view = login_required(AddContactView.as_view())
detail_contact_view = login_required(DetailContactView.as_view())
delete_contact_view = login_required(DeleteContactView.as_view())
edit_function_view = login_required(EditFunctionView.as_view())
edit_contact_view = login_required(EditContactView.as_view())
list_contact_view = login_required(ListContactView.as_view())
