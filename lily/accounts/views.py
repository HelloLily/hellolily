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
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, View
from django.views.generic.edit import UpdateView, DeleteView

from lily.contacts.models import Function, Contact
from lily.notes.models import Note
from lily.search.utils import LilySearch
from lily.utils.functions import flatten, is_ajax
from lily.utils.models.models import PhoneNumber
from lily.utils.views import JsonListView, AngularView
from lily.utils.views.mixins import ExportListViewMixin, LoginRequiredMixin

from .forms import AddAccountQuickbuttonForm, CreateUpdateAccountForm
from .models import Account, Website


class ListAccountView(LoginRequiredMixin, AngularView):
    """
    Display a list of all accounts
    """
    template_name = 'accounts/account_list.html'


class ExportAccountView(ExportListViewMixin, View):
    """

    """
    http_method_names = ['get']
    file_name = 'accounts.csv'

    # ExportListViewMixin
    exportable_columns = {
        'id': {
            'headers': [_('ID')],
            'columns_for_item': ['id']
        },
        'name': {
            'headers': [_('Account')],
            'columns_for_item': ['name']
        },
        'contactInformation': {
            'headers': [
                _('Email'),
                _('Work Phone'),
                _('Mobile Phone'),
                _('Address'),
            ],
            'columns_for_item': [
                'email',
                'phone_work',
                'phone_mobile',
                'address',
            ]
        },
        'assignedTo': {
            'headers': [_('Assigned to')],
            'columns_for_item': ['assigned_to']
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
    def value_for_column(self, account, column):
        try:
            value = account[column]
            if isinstance(value, list):
                value = ', '.join(value)
        except KeyError:
            # Fetch address info from database
            if column == 'address':
                account = Account.objects.get(pk=account['id'])
                address = account.get_addresses().first()
                if address:
                    return '%s %s %s, %s, %s, %s' % (
                        address.street or '',
                        address.street_number or '',
                        address.complement or '',
                        address.postal_code or '',
                        address.city or '',
                        address.country or '',
                    )
            value = ''
        return value

    # ExportListViewMixin
    def get_items(self):
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='accounts_account',
            page=0,
            size=1000000000,
        )
        if self.request.GET.get('export_filter'):
            search.query_common_fields(self.request.GET.get('export_filter'))
        return search.do_search()[0]


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


class DetailAccountView(LoginRequiredMixin, AngularView):
    """
    Display the details of an account.
    """
    template_name = 'accounts/account_detail.html'


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

    def form_invalid(self, form):
        """
        Return a clean html form with annotated form errors.
        """
        context = RequestContext(self.request, self.get_context_data(form=form))
        return HttpResponse(render_to_string('accounts/account_form_ajax.html', context_instance=context))

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '/#/accounts'


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
