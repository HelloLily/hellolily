import anyjson
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
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from lily.accounts.models import Account
from lily.contacts.forms import CreateUpdateContactForm, AddContactQuickbuttonForm
from lily.contacts.models import Contact, Function
from lily.users.models import CustomUser
from lily.utils.functions import is_ajax, clear_messages
from lily.utils.models import PhoneNumber
from lily.utils.templatetags.utils import has_user_in_group

from lily.utils.views import SortedListMixin, FilteredListMixin,\
    DeleteBackAddSaveFormViewMixin, EmailAddressFormSetViewMixin, PhoneNumberFormSetViewMixin,\
    AddressFormSetViewMixin, ValidateFormSetViewMixin, HistoryListViewMixin, ExportListViewMixin,\
    FilteredListByTagMixin


class ListContactView(ExportListViewMixin, SortedListMixin, FilteredListByTagMixin, FilteredListMixin, ListView):
    """
    Display a list of all contacts
    """
    model = Contact
    prefetch_related = [
        'functions__account',
        'email_addresses',
        'phone_numbers',
        'user',
        'tags',
    ]
    sortable = [2, 4, 5, 6]
    default_order_by = 2

    def export_full_name(self, contact):
        return contact.full_name()

    def export_primary_email(self, contact):
        return contact.primary_email()

    def export_work_phone(self, contact):
        return contact.get_work_phone()

    def export_mobile_phone(self, contact):
        return contact.get_mobile_phone()

    def export_account(self, contact):
        try:
            function = contact.get_primary_function()
            return function.account.name
        except AttributeError:
            return None

    def export_tags(self, account):
        return '\r\n'.join([tag.name for tag in account.get_tags()])

    def filter_personal(self):
        return [('full_name', _('personal'))]

    def filter_contact(self):
        return [
            ('primary_email', _('primary e-mail')),
            ('work_phone', _('work phone')),
            ('mobile_phone', _('mobile phone'))
        ]

    def filter_account(self):
        return [('account', _('works at'))]


class DetailContactView(HistoryListViewMixin):
    """
    Display a detail page for a single contact.
    """
    template_name = 'contacts/contact_detail.html'
    model = Contact


class CreateUpdateContactView(PhoneNumberFormSetViewMixin, AddressFormSetViewMixin, ValidateFormSetViewMixin):
    """
    Base class for AddAContactView and EditContactView.
    """

    # Default template and form
    template_name = 'contacts/contact_form.html'
    form_class = CreateUpdateContactForm

    address_form_attrs = {
        'exclude_address_types': ['visiting'],
        'extra_form_kwargs': {
            'initial': {
                'type': 'home',
            }
        }
    }

    def form_valid(self, form):
        self.object = form.save()  # copied from ModelFormMixin

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
            self.template_name = 'contacts/contact_form_ajax.html'

        return super(AddContactView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Handle form submission via AJAX or show custom save message.
        """
        self.object = form.save()  # copied from ModelFormMixin

        message = _('%s (Contact) has been saved.') % self.object.full_name()
        # Show save message
        messages.success(self.request, message)

        if is_ajax(self.request):
            form_kwargs = self.get_form_kwargs()

            # Add e-mail address to contact as primary
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
                redirect_url = reverse('contact_edit', kwargs={
                    'pk': self.object.pk,
                })
            else:  # redirect if in the list view or dashboard
                redirect_url = None
                parse_result = urlparse(self.request.META['HTTP_REFERER'])
                if parse_result.path in (reverse('contact_list'), reverse('dashboard')):
                    redirect_url = self.get_success_url()

            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

        return super(AddContactView, self).form_valid(form)

    def form_invalid(self, form):
        """
        Overloading super().form_invalid to mark the primary checkbox for e-mail addresses as
        checked for postbacks.
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(anyjson.serialize({
                'error': True,
                'html': render_to_string(self.template_name, context_instance=context)
            }), content_type='application/json')

        return super(AddContactView, self).form_invalid(form)

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=5&sort_order=desc' % (reverse('contact_list'))


class EditContactView(DeleteBackAddSaveFormViewMixin, EmailAddressFormSetViewMixin, CreateUpdateContactView, UpdateView):
    """
    View to edit a contact.
    """
    model = Contact

    def form_valid(self, form):
        """
        Save m2m relations to edited contact (i.e. Phone numbers, E-mail addresses and Addresses).
        """
        self.object = form.save()  # copied from ModelFormMixin

        # Show save message
        messages.success(self.request, _('%s (Contact) has been edited.') % self.object.full_name())

        return super(EditContactView, self).form_valid(form)

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=6&sort_order=desc' % (reverse('contact_list'))


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
        messages.success(self.request, _('%s (Contact) has been deleted.') % self.object.full_name())

        self.object.delete()

        redirect_url = self.get_success_url()
        if is_ajax(request):
            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

        return redirect(redirect_url)

    def get_success_url(self):
        return reverse('contact_list')


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
