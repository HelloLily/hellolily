import base64
import pickle
from datetime import date
from hashlib import sha256
from urlparse import urlparse

import anyjson
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from lily.accounts.models import Account
from lily.contacts.forms import CreateUpdateContactForm, AddContactQuickbuttonForm
from lily.contacts.models import Contact, Function
from lily.users.models import CustomUser
from lily.utils.functions import is_ajax, clear_messages
from lily.utils.models import PhoneNumber, SocialMedia
from lily.utils.templatetags.utils import has_user_in_group
from lily.utils.views import DataTablesListView, JsonListView
from lily.utils.views.mixins import SortedListMixin, FilteredListMixin, HistoryListViewMixin, ExportListViewMixin, FilteredListByTagMixin, \
    LoginRequiredMixin


class ListContactView(ExportListViewMixin, SortedListMixin, FilteredListByTagMixin, FilteredListMixin, DataTablesListView):
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

    # SortedlistMixin
    sortable = [1, 3, 4, 5]
    default_order_by = 1

    # DataTablesListView
    columns = SortedDict([
        ('edit', {
            'mData': 'edit',
            'bSortable': False,
        }),
        ('name', {
            'mData': 'name',
        }),
        ('contact', {
            'mData': 'contact',
            # Indeterminable on what to sort
            'bSortable': False,
        }),
        ('works_at', {
            'mData': 'works_at',
        }),
        ('created', {
            'mData': 'created',
            'sClass': 'visible-md visible-lg',
        }),
        ('modified', {
            'mData': 'modified',
            'sClass': 'visible-md visible-lg',
        }),
        ('tags', {
            'mData': 'tags',
            # Generic relations are not sortable on QuerySet.
            'bSortable': False,
        }),
    ])

    # ExportListViewMixin
    exportable_columns = {
        'name': {
            'headers': [_('Name')],
            'columns_for_item': ['name']
        },
        'contact_information': {
            'headers': [
                _('Email'),
                _('Work Phone'),
                _('Mobile Phone'),
            ],
            'columns_for_item': [
                'email',
                'work_phone',
                'mobile_phone',
            ]
        },
        'works_at': {
            'headers': [_('Works at')],
            'columns_for_item': ['works_at']
        },
        'created': {
            'headers': [_('Created')],
            'columns_for_item': ['created']
        },
        'modified': {
            'headers': [_('Modified')],
            'columns_for_item': ['modified']
        },
        'tags': {
            'headers': [_('Tags')],
            'columns_for_item': ['tags']
        },
    }

    # ExportListViewMixin & DataTablesListView
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'tags__name__icontains',
        'email_addresses__email_address__icontains',
    ]

    def order_queryset(self, queryset, column, sort_order):
        """
        Orders the queryset based on given column and sort_order.

        Used by DataTablesListView.
        """
        prefix = ''
        if sort_order == 'desc':
            prefix = '-'
        if column in ('tags', 'created', 'modified'):
            return queryset.order_by('%s%s' % (prefix, column))
        elif column == 'name':
            return queryset.order_by(
                '%slast_name' % prefix,
                '%sfirst_name' % prefix,
            )
        elif column == 'works_at':
            return queryset.order_by(
                '%sfunctions__account' % prefix
            )
        return queryset

    def value_for_column_name(self, contact):
        """
        Used by ExportListViewMixin.
        """
        return contact.full_name()

    def value_for_column_email(self, contact):
        """
        Used by ExportListViewMixin.
        """
        return contact.get_any_email_address()

    def value_for_column_work_phone(self, contact):
        """
        Used by ExportListViewMixin.
        """
        return contact.get_work_phone()

    def value_for_column_mobile_phone(self, contact):
        """
        Used by ExportListViewMixin.
        """
        return contact.get_mobile_phone()

    def value_for_column_works_at(self, contact):
        """
        Used by ExportListViewMixin.
        """
        if contact.functions.count() > 0:
            return contact.functions.all()[0].account
        return None

    def value_for_column_tags(self, contact):
        """
        Used by ExportListViewMixin.
        """
        return ', '.join([tag.name for tag in contact.get_tags()])

    def value_for_column_created(self, contact):
        """
        Used by ExportListViewMixin.
        """
        return contact.created

    def value_for_column_modified(self, contact):
        """
        Used by ExportListViewMixin.
        """
        return contact.modified


class JsonContactListView(LoginRequiredMixin, JsonListView):
    """
    JSON: Display account information for a contact
    """
    # ListView
    model = Contact

    # FilterQuerysetMixin
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'preposition__icontains',
    ]

    # JsonListView
    filter_on_field = 'functions__account__id'


class DetailContactView(HistoryListViewMixin):
    """
    Display a detail page for a single contact.
    """
    template_name = 'contacts/contact_detail.html'
    model = Contact

    def get_queryset(self):
        """
        Prefetch related objects to reduce lazy lookups.
        """
        qs = super(DetailContactView, self).get_queryset()
        qs = qs.prefetch_related('functions__account__functions__contact',
                                 'functions__account__functions__contact__email_addresses',
                                 'functions__account__functions__contact__phone_numbers')
        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(DetailContactView, self).get_context_data(**kwargs)
        kwargs.update({
            'email_count': self.get_emails_list().count(),
        })

        return kwargs


class JsonContactWorksAtView(View):
    """
    JSON: Display account information for a contact
    """

    def get(self, request, pk):
        contact = Contact.objects.get(pk=pk)
        function_list = contact.functions.all()
        works_at = []
        for function in function_list:
            account = function.account
            works_at.append({'name': account.name, 'pk': account.pk})
        response = anyjson.serialize({'works_at': works_at})
        return HttpResponse(response, content_type="application/javascript")


class CreateUpdateContactMixin(LoginRequiredMixin):
    """
    Base class for AddAContactView and EditContactView.
    """
    template_name = 'contacts/contact_form.html'
    form_class = CreateUpdateContactForm

    def form_valid(self, form):
        success_url = super(CreateUpdateContactMixin, self).form_valid(form)

        if form.cleaned_data.get('twitter'):
            twitter = SocialMedia.objects.create(name='twitter', username=form.cleaned_data.get('twitter'))
            self.object.social_media.add(twitter)
        else:
            twitter = self.object.social_media.filter(name='twitter')
            if twitter is not None:
                twitter.delete()

        if form.cleaned_data.get('linkedin'):
            linkedin = SocialMedia.objects.create(name='linkedin', username='', profile_url=form.cleaned_data.get('linkedin'))
            self.object.social_media.add(linkedin)
        else:
            linkedin = self.object.social_media.filter(name='linkedin')
            if linkedin is not None:
                linkedin.delete()

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

        return success_url

    def get_context_data(self, **kwargs):
        """
        Provide a url to go back to.
        """
        kwargs = super(CreateUpdateContactMixin, self).get_context_data(**kwargs)
        if not is_ajax(self.request):
            kwargs.update({
                'back_url': self.get_success_url(),
            })

        return kwargs

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=6&sort_order=desc' % (reverse('contact_list'))


class AddContactView(CreateUpdateContactMixin, CreateView):
    """
    View to add a contact. Also supports a smaller (quickbutton) form for ajax requests.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered for ajax requests.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        self.is_ajax = False
        if is_ajax(request):
            self.is_ajax = True
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

    def get_form_kwargs(self):
        kwargs = super(CreateUpdateContactMixin, self).get_form_kwargs()
        if not self.is_ajax:
            kwargs.update({
                'formset_form_attrs': {
                    'addresses': {
                        'exclude_address_types': ['visiting'],
                        'extra_form_kwargs': {
                            'initial': {
                                'type': 'home',
                            }
                        }
                    }
                }
            })
        return kwargs

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
        return '%s?order_by=4&sort_order=desc' % (reverse('contact_list'))


class EditContactView(CreateUpdateContactMixin, UpdateView):
    """
    View to edit a contact.
    """
    model = Contact

    def form_valid(self, form):
        """
        Save m2m relations to edited contact (i.e. Phone numbers, E-mail addresses and Addresses).
        """
        success_url = super(EditContactView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Contact) has been edited.') % self.object.full_name())

        return success_url

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=5&sort_order=desc' % (reverse('contact_list'))


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
json_contact_works_at_view = login_required(JsonContactWorksAtView.as_view())
delete_contact_view = login_required(DeleteContactView.as_view())
edit_contact_view = login_required(EditContactView.as_view())
list_contact_view = login_required(ListContactView.as_view())

