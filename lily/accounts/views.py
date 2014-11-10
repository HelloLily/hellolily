from urlparse import urlparse

import anyjson
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, View
from django.views.generic.edit import UpdateView, DeleteView

from lily.accounts.forms import AddAccountQuickbuttonForm, CreateUpdateAccountForm
from lily.accounts.models import Account, Website
from lily.contacts.models import Function, Contact
from lily.notes.models import Note
from lily.utils.functions import flatten, is_ajax
from lily.utils.models import PhoneNumber
from lily.utils.views import DataTablesListView, JsonListView
from lily.utils.views.mixins import (SortedListMixin, FilteredListMixin, HistoryListViewMixin, ExportListViewMixin,
                                     FilteredListByTagMixin, LoginRequiredMixin)


class ListAccountView(ExportListViewMixin, SortedListMixin, FilteredListByTagMixin, FilteredListMixin, DataTablesListView):
    model = Account
    prefetch_related = [
        'phone_numbers',
        'tags',
    ]

    # SortedListMixin
    sortable = [1, 3, 4]
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
        'account': {
            'headers': [_('Account')],
            'columns_for_item': ['account']
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
        'name__icontains',
        'tags__name__icontains',
        # TODO: Searching trough relations doesn't work on large datasets
        # 'phone_numbers__number__icontains',
        # 'email_addresses__email_address__icontains',
    ]

    def get_queryset(self):
        return super(ListAccountView, self).get_queryset().filter(is_deleted=False)

    def order_queryset(self, queryset, column, sort_order):
        """
        Orders the queryset based on given column and sort_order.

        Used by DataTablesListView.
        """
        prefix = ''
        if sort_order == 'desc':
            prefix = '-'
        if column in ('name', 'tags', 'created', 'modified'):
            return queryset.order_by('%s%s' % (prefix, column))
        return queryset

    def value_for_column_account(self, account):
        """
        Used by ExportListViewMixin.
        """
        return account.name

    def value_for_column_email(self, account):
        """
        Used by ExportListViewMixin.
        """
        return account.get_any_email_address()

    def value_for_column_work_phone(self, account):
        """
        Used by ExportListViewMixin.
        """
        return account.get_work_phone()

    def value_for_column_mobile_phone(self, account):
        """
        Used by ExportListViewMixin.
        """
        return account.get_mobile_phone()

    def value_for_column_tags(self, account):
        """
        Used by ExportListViewMixin.
        """
        return ', '.join([tag.name for tag in account.get_tags()])

    def value_for_column_created(self, account):
        """
        Used by ExportListViewMixin.
        """
        return account.created

    def value_for_column_modified(self, account):
        """
        Used by ExportListViewMixin.
        """
        return account.modified


class JsonAccountListView(LoginRequiredMixin, JsonListView):
    """
    JSON: Display account information for a contact
    """
    # ListView
    model = Account

    # FilterQuerysetMixin
    search_fields = [
        'name__icontains',
    ]

    # JsonListView
    filter_on_field = 'functions__contact__id'

    def get_queryset(self):
        queryset = super(JsonAccountListView, self).get_queryset()
        return queryset.filter(is_deleted=False)


class DetailAccountView(LoginRequiredMixin, HistoryListViewMixin):
    """
    Display a detail page for a single account.
    """
    model = Account

    def dispatch(self, request, *args, **kwargs):
        """
        This is a copy from HistoryListViewMixin.
        """
        if is_ajax(request):
            self.template_name = 'utils/historylist.html'

        return super(DetailAccountView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Prefetch related objects to reduce lazy lookups.
        """
        qs = super(DetailAccountView, self).get_queryset()
        qs = qs.prefetch_related('functions__contact__functions',
                                 'functions__contact__email_addresses',
                                 'functions__contact__phone_numbers')
        return qs

    def get_notes_list(self, filter_date):
        """
        Returns an object list containing all notes and all messages related
        to this Account. For the Account overview we also want to show all
        notes and messages related to Contacts related to this Account.

        Arguments:
            filter_date (datetime): date before the message must be sent.

        Returns:
            A filtered Notes QuerySet.
        """
        account_content_type = ContentType.objects.get_for_model(self.model)
        contact_content_type = ContentType.objects.get_for_model(Contact)

        contact_ids = Contact.objects.filter(functions__account_id=self.object.pk).values_list('pk', flat=True)

        # Build initial list with just notes.
        # TODO: replace _default_manager with objects when Polymorphic works.
        notes_list = Note._default_manager.filter(
            (
                Q(content_type=account_content_type) &
                Q(object_id=self.object.pk)
            ) |
            (
                Q(content_type=contact_content_type) &
                Q(object_id__in=contact_ids)
            )
        ).filter(is_deleted=False)

        if filter_date:
            notes_list = notes_list.filter(sort_by_date__lt=filter_date)

        return notes_list

    def get_related_email_addresses_for_object(self):
        # Get email addresses from related contacts.
        email_address_list = []
        for contact in self.object.get_contacts():
            email_address_list.extend(contact.email_addresses.all())

        # Add email addresses of Account.
        email_address_list.extend(self.object.email_addresses.all())

        return email_address_list

    def get_context_data(self, **kwargs):
        kwargs = super(DetailAccountView, self).get_context_data(**kwargs)
        kwargs.update({
            'email_count': self.get_emails_list().count(),
        })

        return kwargs


class CreateUpdateAccountMixin(LoginRequiredMixin):
    """
    Base class for AddAccountView and EditAccountView.
    """
    form_class = CreateUpdateAccountForm
    model = Account

    def post(self, request, *args, **kwargs):
        """
        Overloading super().post to filter http:// as non provided value for the website field.
        Drawback: http:// dissappears from the input fields on postbacks.
        """
        post_data = request.POST.copy()
        if post_data.get('website') and post_data['website'] == 'http://':
            post_data['website'] = ''

        if post_data.get('primary_website') and post_data['primary_website'] == 'http://':
            post_data['primary_website'] = ''

        request.POST = post_data

        return super(CreateUpdateAccountMixin, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        success_url = super(CreateUpdateAccountMixin, self).form_valid(form)

        if not is_ajax(self.request):
            form_kwargs = self.get_form_kwargs()
            # Save primary website
            if form_kwargs['data'].get('primary_website'):

                try:
                    website = self.object.websites.get(is_primary=True)
                    website.website = form_kwargs['data'].get('primary_website')
                    website.save()
                except Website.DoesNotExist:
                    Website.objects.create(account=self.object, is_primary=True,
                                           website=form_kwargs['data'].get('primary_website'))
            # Remove possible primary website
            else:
                try:
                    website = Website.objects.filter(account=self.object, is_primary=True)
                    website.delete()
                except Exception:
                    pass

        return success_url

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateAccountMixin, self).get_context_data(**kwargs)
        if not is_ajax(self.request):
            kwargs.update({
                'back_url': self.get_success_url(),
            })

        return kwargs


class AddAccountView(CreateUpdateAccountMixin, CreateView):
    """
    View to add an acccount. Also supports a smaller (quickbutton) form for ajax requests.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered for ajax requests.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        self.is_ajax = False
        if is_ajax(request):
            self.is_ajax = True
            self.form_class = AddAccountQuickbuttonForm
            self.template_name = 'accounts/account_form_ajax.html'

        return super(AddAccountView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateUpdateAccountMixin, self).get_form_kwargs()
        if not self.is_ajax:
            kwargs.update({
                'formset_form_attrs': {
                    'addresses': {
                        'exclude_address_types': ['home', ],
                        'extra_form_kwargs': {
                            'initial': {
                                'type': 'visiting',
                            }
                        }
                    }
                }
            })
        return kwargs

    def form_valid(self, form):
        """
        Handle form submission via AJAX or show custom save message.
        """
        self.object = form.save()  # copied from ModelFormMixin
        message = _('%s (Account) has been saved.') % self.object.name
        # Show save message
        messages.success(self.request, message)

        if is_ajax(self.request):
            form_kwargs = self.get_form_kwargs()

            # Save website
            if form.cleaned_data.get('website'):
                Website.objects.create(website=form.cleaned_data.get('website'),
                                       account=self.object, is_primary=True)

            # Add e-mail address to account as primary
            self.object.primary_email = form.cleaned_data.get('primary_email')
            self.object.save()

            # Save phone number
            if form.cleaned_data.get('phone_number'):
                phone = PhoneNumber.objects.create(raw_input=form.cleaned_data.get('phone_number'))
                self.object.phone_numbers.add(phone)

            # Check if the user wants to 'add & edit'
            submit_action = form_kwargs['data'].get('submit_button', None)
            if submit_action == 'edit':
                redirect_url = reverse('account_edit', kwargs={
                    'pk': self.object.pk,
                })
            else:  # redirect if in the list view or dashboard
                redirect_url = None
                parse_result = urlparse(self.request.META['HTTP_REFERER'])
                if parse_result.path in (reverse('account_list'), reverse('dashboard')):
                    redirect_url = self.get_success_url()

            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

        return super(AddAccountView, self).form_valid(form)

    def form_invalid(self, form):
        """
        Overloading super().form_invalid to return a different response to ajax requests.
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(anyjson.serialize({
                'error': True,
                'html': render_to_string(self.template_name, context_instance=context)
            }), content_type='application/json')

        return super(AddAccountView, self).form_invalid(form)

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=3&sort_order=desc' % (reverse('account_list'))


class EditAccountView(CreateUpdateAccountMixin, UpdateView):
    """
    View to edit an acccount.
    """
    model = Account

    def form_valid(self, form):
        """
        Show custom success message.
        """
        success_url = super(EditAccountView, self).form_valid(form)
        messages.success(self.request, _('%s (Account) has been edited.') % self.object.name)

        return success_url

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=4&sort_order=desc' % (reverse('account_list'))


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Account

    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        self.object = self.get_object()
        self.object.email_addresses.remove()
        self.object.addresses.remove()
        self.object.phone_numbers.remove()
        self.object.tags.remove()

        functions = Function.objects.filter(account=self.object)
        functions.delete()

        # Show delete message
        messages.success(self.request, _('%s (Account) has been deleted.') % self.object.name)

        self.object.delete()

        # TODO: check for contacts and websites ..

        redirect_url = self.get_success_url()
        if is_ajax(request):
            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

        return redirect(redirect_url)

    def get_success_url(self):
        return reverse('account_list')


class ExistsAccountView(LoginRequiredMixin, View):
    """
    Check whether an account exists based on slugs.
    """
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # Check if an account can be found using slugified names
        name = kwargs.pop('account_name')
        flattened = flatten(name)

        exists = False
        edit_url = None
        accounts = Account.objects.filter(flatname=flattened)
        if accounts.exists():
            account = accounts[0]
            exists = True
            edit_url = reverse('account_edit', kwargs={'pk': account.pk})
        else:
            raise Http404()

        return HttpResponse(anyjson.serialize({
            'exists': exists,
            'edit_url': edit_url
        }), content_type='application/json')
