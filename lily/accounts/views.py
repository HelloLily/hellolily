from urlparse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.html import escapejs
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, View
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.list import ListView

from lily.accounts.forms import AddAccountQuickbuttonForm, CreateUpdateAccountForm
from lily.accounts.models import Account, Website
from lily.contacts.models import Function
from lily.notes.views import HistoryListViewMixin
from lily.utils.functions import flatten, is_ajax
from lily.utils.models import PhoneNumber
from lily.utils.templatetags.messages import tag_mapping
from lily.utils.templatetags.utils import has_user_in_group
from lily.utils.views import SortedListMixin, FilteredListMixin,\
    EmailAddressFormSetViewMixin, PhoneNumberFormSetViewMixin, WebsiteFormSetViewMixin,\
    AddressFormSetViewMixin, DeleteBackAddSaveFormViewMixin, ValidateFormSetViewMixin


class ListAccountView(SortedListMixin, FilteredListMixin, ListView):
    template_name = 'accounts/mwsadmin/model_list.html'
    sortable = [2, 4, 5]
    model = Account
    prefetch_related = [
        'phone_numbers',
        'tags',
        'user'
    ]
    default_order_by = 2

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListAccountView, self).get_context_data(**kwargs)

        kwargs.update({
            'list_item_template': 'accounts/mwsadmin/model_list_item.html',
        })

        return kwargs


class DetailAccountView(HistoryListViewMixin):
    """
    Display a detail page for a single account.
    """
    template_name = 'accounts/mwsadmin/details.html'
    model = Account
    success_url_reverse_name = 'account_details'


class CreateUpdateAccountView(DeleteBackAddSaveFormViewMixin, EmailAddressFormSetViewMixin, PhoneNumberFormSetViewMixin, AddressFormSetViewMixin, WebsiteFormSetViewMixin, ValidateFormSetViewMixin):
    """
    Base class for AddAccountView and EditAccountView.
    """
    # Default template and form
    template_name = 'accounts/create_or_update.html'
    form_class = CreateUpdateAccountForm

    # Option for address formset
    exclude_address_types = ['home']

    def dispatch(self, request, *args, **kwargs):
        # Override default formset template to adjust choices for address_type
        #self.formset_data.update({'addresses_formset': {'template': 'accounts/mwsadmin/formset_address.html'}})
        self.formset_data.update({'websites_formset': {'label': _('Extra websites')}})

        return super(CreateUpdateAccountView, self).dispatch(request, *args, **kwargs)

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

        return super(CreateUpdateAccountView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()  # copied from ModelFormMixin

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

        return super(CreateUpdateAccountView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateAccountView, self).get_context_data(**kwargs)
        kwargs.update({
            'back_url': self.get_success_url(),
        })

        return kwargs


class AddAccountView(CreateUpdateAccountView, CreateView):
    """
    View to add an acccount. Also supports a smaller (quickbutton) form for ajax requests.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered for ajax requests.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        if is_ajax(request):
            self.form_class = AddAccountQuickbuttonForm
            self.template_name = 'accounts/mwsadmin/quickbutton_form.html'

        return super(AddAccountView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Handle form submission via AJAX or show custom save message.
        """
        self.object = form.save()  # copied from ModelFormMixin
        message = _('%s (Account) has been saved.') % self.object.name

        if is_ajax(self.request):
            form_kwargs = self.get_form_kwargs()

            # Save website
            if form.cleaned_data.get('website'):
                Website.objects.create(website=form.cleaned_data.get('website'),
                                       account=self.object, is_primary=True)

            # Add e-mail address to account as primary
            self.object.primary_email = form.cleaned_data.get('email')
            self.object.save()

            # Save phone number
            if form.cleaned_data.get('phone'):
                phone = PhoneNumber.objects.create(raw_input=form.cleaned_data.get('phone'))
                self.object.phone_numbers.add(phone)

            # Check if the user wants to 'add & edit'
            submit_action = form_kwargs['data'].get('submit_button', None)
            if submit_action == 'edit':
                do_redirect = True
                url = reverse('account_edit', kwargs={
                    'pk': self.object.pk,
                })
                notification = False
                html_response = ''
            else:  # redirect if in the list view or dashboard
                url_obj = urlparse(self.request.META['HTTP_REFERER'])
                if url_obj.path.endswith(reverse('account_list')) or url_obj.path == reverse('dashboard'):
                    # Show save message
                    messages.success(self.request, message)

                    do_redirect = True
                    if url_obj.path.endswith(reverse('account_list')):
                        url = '%s?order_by=4&sort_order=desc' % reverse('account_list')
                    else:
                        url = self.request.META['HTTP_REFERER']
                    notification = False
                    html_response = ''
                else:
                    do_redirect = False
                    url = ''
                    html_response = ''
                    notification = [{'message': escapejs(message), 'tags': tag_mapping.get('success')}]

            # Return response
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': html_response,
                'redirect': do_redirect,
                'notification': notification,
                'url': url
            }), mimetype='application/json')

        # Show save message
        messages.success(self.request, message)

        return super(AddAccountView, self).form_valid(form)

    def form_invalid(self, form):
        """
        Overloading super().form_invalid to return a different response to ajax requests. For normal
        request.
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                'error': True,
                'html': render_to_string(self.template_name, context_instance=context)
            }), mimetype='application/json')

        return super(AddAccountView, self).form_invalid(form)

    def get_success_url(self):
        """
        Redirect to the list view, ordered by created
        """
        return '%s?order_by=4&sort_order=desc' % (reverse('account_list'))


class EditAccountView(CreateUpdateAccountView, UpdateView):
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
        Redirect to the list view, ordered by last modified.
        """
        return '%s?order_by=5&sort_order=desc' % (reverse('account_list'))


class DeleteAccountView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Account
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        self.object = self.get_object()

        # Check this account isn't linked to a user in an admin group.
        if has_user_in_group(self.object, 'account_admin'):
            raise Http404()

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

        return redirect(reverse('account_list'))


class ExistsAccountView(View):
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

        return HttpResponse(simplejson.dumps({
            'exists': exists,
            'edit_url': edit_url
        }), mimetype='application/json')


# Perform logic here instead of in urls.py
add_account_view = login_required(AddAccountView.as_view())
detail_account_view = login_required(DetailAccountView.as_view())
delete_account_view = login_required(DeleteAccountView.as_view())
edit_account_view = login_required(EditAccountView.as_view())
list_account_view = login_required(ListAccountView.as_view())
exist_account_view = login_required(ExistsAccountView.as_view())
