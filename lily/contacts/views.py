from datetime import date
from hashlib import sha256
from urlparse import urlparse
import base64
import pickle

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.html import escapejs
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from lily.accounts.models import Account
from lily.contacts.forms import CreateUpdateContactForm, AddContactQuickbuttonForm
from lily.contacts.models import Contact, Function
from lily.notes.views import NoteDetailViewMixin
from lily.users.models import CustomUser
from lily.utils.functions import is_ajax, clear_messages
from lily.utils.models import PhoneNumber
from lily.utils.templatetags.messages import tag_mapping
from lily.utils.templatetags.utils import has_user_in_group
from lily.utils.views import SortedListMixin, FilteredListMixin,\
    DeleteBackAddSaveFormViewMixin, EmailAddressFormSetViewMixin, PhoneNumberFormSetViewMixin,\
    AddressFormSetViewMixin, ValidateFormSetViewMixin, ValidateEmailAddressFormSetViewMixin


class ListContactView(SortedListMixin, FilteredListMixin, ListView):
    """
    Display a list of all contacts
    """
    template_name = 'contacts/model_list.html'
    model = Contact
    sortable = [2, 4, 5, 6]
    default_order_by = 2

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListContactView, self).get_context_data(**kwargs)

        kwargs.update({
            'list_item_template': 'contacts/model_list_item.html',
        })
        return kwargs


class DetailContactView(NoteDetailViewMixin):
    """
    Display a detail page for a single contact.
    """
    template_name = 'contacts/details.html'
    model = Contact
    success_url_reverse_name = 'contact_details'


class CreateUpdateContactView(PhoneNumberFormSetViewMixin, AddressFormSetViewMixin, ValidateFormSetViewMixin):
    """
    Base class for AddAContactView and EditContactView.
    """

    # Default template and form
    template_name = 'contacts/create_or_update.html'
    form_class = CreateUpdateContactForm
    
    exclude_address_types = ['visiting']
    
    def __init__(self, *args, **kwargs):
        super(CreateUpdateContactView, self).__init__(*args, **kwargs)
        
        # Override default formset template to adjust choices for address_type
        self.formset_data['addresses_formset']['template'] = 'contacts/formset_address.html'

    def form_valid(self, form):
        # Copied from ModelFormMixin
        self.object = form.save()
        
        if not is_ajax(self.request):
            form_kwargs = self.get_form_kwargs()
            
            # Save selected account
            if form_kwargs['data'].get('account'):
                pk = form_kwargs['data'].get('account')
                account = Account.objects.get(pk=pk)
                Function.objects.get_or_create(account=account, contact=self.object)
    
                functions = Function.objects.filter(~Q(account_id=pk), Q(contact=self.object))
                functions.delete()
            else:
                # No account selected
                functions = Function.objects.filter(contact=self.object)
                functions.delete()
                
        return super(CreateUpdateContactView, self).form_valid(form)


class AddContactView(DeleteBackAddSaveFormViewMixin, EmailAddressFormSetViewMixin, CreateUpdateContactView, CreateView):
    """
    View to add a contact. Also supports a smaller (quickbutton) form for ajax requests.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered for ajax requests.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        if is_ajax(request):
            self.form_class = AddContactQuickbuttonForm
            self.template_name = 'contacts/quickbutton_form.html'
        
        return super(AddContactView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Handle form submission via AJAX or show custom save message.
        """
        # Save instance
        super(AddContactView, self).form_valid(form)
        message = _('%s (Contact) has been saved.') % self.object.full_name()

        if is_ajax(self.request):
            form_kwargs = self.get_form_kwargs()
            
            # Add e-mail address to account as primary
            self.object.primary_email = form.cleaned_data.get('email')
            self.object.save()

            # Save phone number
            if form.cleaned_data.get('phone'):
                phone = PhoneNumber.objects.create(raw_input=form.cleaned_data.get('phone'))
                self.object.phone_numbers.add(phone)

            # Save account
            if form_kwargs['data'].get('account'):
                pk = form_kwargs['data'].get('account')
                account = Account.objects.get(pk=pk)
                Function.objects.get_or_create(account=account, contact=self.object)

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
                # Redirect if in the list view or dashboard
                url_obj = urlparse(self.request.META['HTTP_REFERER'])
                if url_obj.path.endswith(reverse('contact_list')) or url_obj.path == reverse('dashboard'):
                    # Show save message
                    messages.success(self.request, message)

                    do_redirect = True
                    if url_obj.path.endswith(reverse('contact_list')):
                        url = '%s?order_by=5&sort_order=desc' % reverse('contact_list')
                    else:
                        url = self.request.META['HTTP_REFERER']
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
                
        # Show save message
        messages.success(self.request, message);
        
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
        
        return super(AddContactView, self).form_invalid(form)

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return redirect('%s?order_by=5&sort_order=desc' % (reverse('contact_list')))


class EditContactView(DeleteBackAddSaveFormViewMixin, ValidateEmailAddressFormSetViewMixin, CreateUpdateContactView, UpdateView):
    """
    View to edit a contact.
    """
    model = Contact

    def form_valid(self, form):
        """
        Save m2m relations to edited contact (i.e. Phone numbers, E-mail addresses and Addresses).
        """
        super(EditContactView, self).form_valid(form)

        # TODO: make this work with the new way of using formsets
#        # Save all e-mail address, phone number and address formsets
#        if self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
#            form_kwargs = self.get_form_kwargs()
#            # Save form
#            super(EditContactView, self).form_valid(form)
#
#            # Handle e-mail addresses permission checks
#            allow_edit_email = email_verify = False
#            allow_save = False
#            is_user_contact = True
#            primary_has_changed = False
#            verification_email_data = None
#            new_primary_email_address_instance = None
#            old_primary_email_address_instance = None
#            
#            # TODO: move the permission logic to a decorator for this view
#
#            # Permission check: users in a certain group and the contact's user can edit e-mail adresses
#            # For e-mailaddresses a confirmation e-mail is sent to the new e-mail adres when
#            # the contact's user changes it. Another user with permissions can change it regardless.
####            try:
####                user = CustomUser.objects.get(contact=self.object)
####            except CustomUser.DoesNotExist:
####                # If it's not a user's contact
####                allow_edit_email = True
####                is_user_contact = False
####            else:
####                if user == self.request.user:
####                    # If this is the case, allow editing it after verification via e-mail
####                    allow_edit_email = email_verify = True
####                elif 'account_admin' in self.request.user.groups.values_list('name', flat=True):
####                    # Users in this group can always edit e-mail addresses
####                    allow_edit_email = True
#
#            # Handle saving (and sending verification e-mails for) e-mail addresses
#            if allow_edit_email:
#                # Find the e-mail address marked as primary e-mail address
#                primary_email_prefix = form_kwargs['data'].get(self.email_addresses_formset.prefix + '_primary-email')
#                
#                # Loop through all e-mail addresses
#                for formset in self.email_addresses_formset:
#                    # Check if formset instance should be deleted
####                    if form_kwargs['data'].get(formset.prefix + '-DELETE'):
####                        # Only delete if it's not a user's contact or if it's not marked as primary e-mail when it is a user's contact
####                        if not is_user_contact or formset.prefix != primary_email_prefix: 
####                            self.object.email_addresses.remove(formset.instance)
####                            formset.instance.delete()
####                        elif is_user_contact:
####                            # Add message
####                            messages.error(self.request, _('The e-mail address %s was not removed because it\'s the login for this user.' % formset.instance.email_address))
####                        continue
#
#                    # Explicitly set 'is_primary' on every e-mail address to make sure only one is 
#                    # marked as primary e-mail.
#                    if formset.prefix == primary_email_prefix:
#                        formset.instance.is_primary = True
#                    else:
#                        formset.instance.is_primary = False
#
#                    # Only save e-mail address if something else than is_primary/status was filled in
#                    if formset.instance.email_address:
#                        # If it's an existing e-mail address and the address itself has not changed,
#                        # allow saving it regardless of other attributes that might have changed. 
#                        # This prevents existing e-mail addresses that are no longer the primary
#                        # e-mail address from demanding verification as well as the new ones. 
#                        if formset.instance.pk:
#                            existing_email_address = EmailAddress.objects.get(pk=formset.instance.pk)
#                            if existing_email_address.email_address == formset.instance.email_address:
#                                allow_save = True
#                                
#                            # Check if the attribute 'is_primary' has changed or if the e-mail address itself has been modified
#                            if existing_email_address.is_primary != formset.instance.is_primary:
#                                primary_has_changed = True
#                                if formset.instance.is_primary:
#                                    new_primary_email_address_instance = formset.instance
#                                else:
#                                    old_primary_email_address_instance = existing_email_address
#                            elif existing_email_address.email_address != formset.instance.email_address:
#                                primary_has_changed = True
#                                new_primary_email_address_instance = formset.instance
#                                old_primary_email_address_instance = existing_email_address
#                        
#                        # Simply save the e-mail address if none of the permission checks is
#                        # blocking this action.
#                        if allow_save or not email_verify:
#                            if not primary_has_changed:
#                                formset.save()
#                                self.object.email_addresses.add(formset.instance)
#                
#                if old_primary_email_address_instance != None:
#                    if not allow_save and email_verify or primary_has_changed:
#                        # Get contact pk
#                        pk = self.object.pk
#                        
#                        # Calculate expire date
#                        expire_date = date.today() + timedelta(days=settings.EMAIL_CONFIRM_TIMEOUT_DAYS)
#                        expire_date_pickled = pickle.dumps(expire_date)
#        
#                        # Get link to site
#                        protocol = self.request.is_secure() and 'https' or 'http'
#                        site = Site.objects.get_current()
#        
#                        # Build data dict
#                        verification_email_data = base64.urlsafe_b64encode(pickle.dumps({
#                            'contact_pk': self.object.pk,
#                            'old_email_address': old_primary_email_address_instance.email_address,
#                            'email_address': pickle.dumps(new_primary_email_address_instance),
#                            'expire_date': expire_date_pickled,
#                            'hash': sha256('%s%s%d%s' % (old_primary_email_address_instance.email_address, new_primary_email_address_instance.email_address, pk, expire_date_pickled)).hexdigest(),
#                        })).strip('=')
#        
#                        # Build verification link
#                        verification_link = "%s://%s%s" % (protocol, site, reverse('contact_confirm_email', kwargs={
#                            'data': verification_email_data
#                        }))
#        
#                        # Sent an e-mail informing the user his primary e-mail address
#                        # can be changed.
#                        send_templated_mail(
#                            template_name='email_confirm',
#                            from_email=settings.DEFAULT_FROM_EMAIL,
#                            recipient_list=[old_primary_email_address_instance.email_address, new_primary_email_address_instance.email_address],
#                            context = {
#                                'current_site': site,
#                                'full_name': self.object.full_name(),
#                                'verification_link': verification_link,
#                                'email_address': new_primary_email_address_instance.email_address
#                            }
#                        )
#        
#                        # Add message
#                        messages.info(self.request, _('An e-mail was sent to %s with a link to verify your new primary e-mail address.' % formset.instance.email_address))
#            else:
#                # Add message
#                messages.error(self.request, _('You don\'t have enough permissions to change the e-mail addresses for %.' % self.object.full_name()))

        # Show save message
        messages.success(self.request, _('%s (Contact) has been edited.') % self.object.full_name());

        return self.get_success_url()

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return redirect('%s?order_by=6&sort_order=desc' % (reverse('contact_list')))


class DeleteContactView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Contact
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        self.object = self.get_object()
        
        # Check this contact isn't linked to a user in an admin group.
        if has_user_in_group(self.object, 'account_admin'):
            raise Http404()
        
        self.object.email_addresses.remove()
        self.object.addresses.remove()
        self.object.phone_numbers.remove()
        self.object.tags.remove()

        functions = Function.objects.filter(contact=self.object)
        functions.delete()

        # Show delete message
        messages.success(self.request, _('%s (Contact) has been deleted.') % self.object.full_name());

        self.object.delete()

        return redirect(reverse('contact_list'))


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
           
            # Get user by contact
            contact_pk = data.get('contact_pk')
            user = CustomUser.objects.get(contact_id=contact_pk)

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
                # Add message
                messages.info(self.request, _('You can log in now with your new primary e-mail address.'))
                
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
        old_email = data.get('old_email_address')

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
edit_contact_view = login_required(EditContactView.as_view())
list_contact_view = login_required(ListContactView.as_view())
