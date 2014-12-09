from urlparse import urlparse

import anyjson
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from lily.accounts.models import Account
from lily.search.utils import LilySearch
from lily.utils.functions import is_ajax
from lily.utils.models import PhoneNumber
from lily.utils.views import JsonListView, AngularView
from lily.utils.views.mixins import (HistoryListViewMixin, LoginRequiredMixin, ExportListViewMixin)

from .forms import CreateUpdateContactForm, AddContactQuickbuttonForm
from .models import Contact, Function


class ListContactView(LoginRequiredMixin, AngularView):
    """
    Display a list of all contacts
    """
    template_name = 'contacts/contact_list.html'


class ExportContactView(LoginRequiredMixin, ExportListViewMixin, View):

    http_method_names = ['get']
    file_name = 'contacts.csv'

    # ExportListViewMixin
    exportable_columns = {
        'id': {
            'headers': [_('ID')],
            'columns_for_item': ['id']
        },
        'name': {
            'headers': [_('Name')],
            'columns_for_item': ['name']
        },
        'contactInformation': {
            'headers': [
                _('Email'),
                _('Work Phone'),
                _('Mobile Phone'),
            ],
            'columns_for_item': [
                'email',
                'phone_work',
                'phone_mobile',
            ]
        },
        'worksAt': {
            'headers': [_('Works at')],
            'columns_for_item': ['account_name']
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
            'columns_for_item': ['tag']
        },
    }

    # ExportListViewMixin
    def value_for_column(self, contact, column):
        try:
            value = contact[column]
            if isinstance(value, list):
                value = ', '.join(value)
        except KeyError:
            value = ''
        return value

    # ExportListViewMixin
    def get_items(self):
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='contacts_contact',
        )

        return search.raw_query(query=self.request.GET.get('export_filter'))[0]


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

    def get_queryset(self):
        queryset = super(JsonContactListView, self).get_queryset()
        return queryset.filter(is_deleted=False)


class DetailContactView(LoginRequiredMixin, HistoryListViewMixin):
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


class CreateUpdateContactMixin(LoginRequiredMixin):
    """
    Base class for AddAContactView and EditContactView.
    """
    template_name = 'contacts/contact_form.html'
    form_class = CreateUpdateContactForm

    def form_valid(self, form):
        success_url = super(CreateUpdateContactMixin, self).form_valid(form)

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

        if self.is_ajax:
            form_kwargs = self.get_form_kwargs()

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
                # Redirect to Account if quick create modal from Account.
                elif account and parse_result.path == reverse('account_details', args=(account.pk,)):
                    redirect_url = reverse('account_details', args=(account.pk,))

            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

        return super(AddContactView, self).form_valid(form)

    def get_initial(self):
        """
        Set the initials for the form
        """
        initial = super(AddContactView, self).get_initial()

        # If the Contact is created from an Account, initialize the form with data from that Account
        account_pk = self.kwargs.get('account_pk', None)
        if account_pk:
            try:
                account = Account.objects.get(pk=account_pk)
            except Account.DoesNotExist:
                pass
            else:
                initial.update({'account': account})

        return initial

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
        if self.is_ajax:
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(anyjson.serialize({
                'error': True,
                'html': render_to_string(self.template_name, context_instance=context)
            }), content_type='application/json')

        return super(AddContactView, self).form_invalid(form)

    def get_success_url(self):
        """
        Get the url to redirect to after this form has successfully been submitted.
        """
        return reverse('contact_list')


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


class DeleteContactView(LoginRequiredMixin, DeleteView):
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
