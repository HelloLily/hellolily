from urlparse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
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

from lily.accounts.forms import AddAccountForm, AddAccountMinimalForm, EditAccountForm, \
    WebsiteBaseForm
from lily.accounts.models import Account, Website
from lily.contacts.models import Function
from lily.utils.forms import EmailAddressBaseForm, AccountAddressForm, PhoneNumberBaseForm
from lily.utils.functions import flatten, is_ajax
from lily.utils.models import SocialMedia, EmailAddress, Address, PhoneNumber, COUNTRIES
from lily.utils.templatetags.messages import tag_mapping
from lily.utils.templatetags.utils import has_user_in_group
from lily.utils.views import DetailNoteFormView, SortedListMixin, FilteredListMixin


class ListAccountView(SortedListMixin, FilteredListMixin, ListView):
    template_name = 'accounts/model_list.html'
    model = Account
    sortable = [2, 4, 5]
    default_order_by = 2

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListAccountView, self).get_context_data(**kwargs)

        kwargs.update({
            'list_item_template': 'accounts/model_list_item.html',
        })
        
        return kwargs


class DetailAccountView(DetailNoteFormView):
    """
    Display a detail page for a single account.
    """
    template_name = 'accounts/details.html'
    model = Account
    success_url_reverse_name = 'account_details'


class AddAccountView(CreateView):
    """
    View to add an acccount with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets. Also supports a smaller
    form for ajax requests.
    """
    # Default template and form
    template_name = 'accounts/create_or_update.html'
    form_class = AddAccountForm

    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        if is_ajax(request):
            self.form_class = AddAccountMinimalForm
            self.template_name = 'accounts/quickbutton_form.html'
        else:
            self.WebsiteFormSet = modelformset_factory(Website, form=WebsiteBaseForm, extra=0)
            self.EmailAddressFormSet = modelformset_factory(EmailAddress, form=EmailAddressBaseForm, extra=0)
            self.AddressFormSet = modelformset_factory(Address, form=AccountAddressForm, extra=0)
            self.PhoneNumberFormSet = modelformset_factory(PhoneNumber, form=PhoneNumberBaseForm, extra=0)

        return super(AddAccountView, self).dispatch(request, *args, **kwargs)

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

        return super(AddAccountView, self).post(request, *args, **kwargs)

    def get_form(self, form_class):
        """
        Overloading super().get_form to instantiate formsets while instantiating the form.
        """
        form = super(AddAccountView, self).get_form(form_class)

        # Instantiate the formsets for the normal form
        if not is_ajax(self.request):
            self.websites_formset = form.websites_formset = self.WebsiteFormSet(self.request.POST or None, queryset=Website.objects.none(), prefix='websites')
            self.email_addresses_formset = form.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=EmailAddress.objects.none(), prefix='email_addresses')
            self.addresses_formset = form.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=Address.objects.none(), prefix='addresses')
            self.phone_numbers_formset = form.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=PhoneNumber.objects.none(), prefix='phone_numbers')

        return form

    def form_valid(self, form):
        """
        Add m2m relations to newly created account (i.e. Social media, Phone numbers,
        E-mail addresses and Addresses).
        """
        # Save instance
        super(AddAccountView, self).form_valid(form)

        form_kwargs = self.get_form_kwargs()

        if is_ajax(self.request):
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
            else:
                message = _('%s (Account) has been saved.') % self.object.name

                # Redirect if in the list view or dashboard
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
            if self.websites_formset.is_valid() and self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
                # Handle websites
                for formset in self.websites_formset:
                    # Only save website if more than initial was filled in
                    if formset.instance.website and not formset.instance.website == formset.fields['website'].initial:
                        formset.instance.account = self.object
                        formset.save()

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

            # Add primary website
            if form_kwargs['data'].get('primary_website'):
                try:
                    website = self.object.websites.get(is_primary=True)
                    website.website = form_kwargs['data'].get('primary_website')
                    website.save()
                except Website.DoesNotExist:
                    Website.objects.create(account=self.object, is_primary=True,
                                           website = form_kwargs['data'].get('primary_website'))

#            # Add relation to Facebook
#            if form_kwargs['data'].get('facebook'):
#                facebook = SocialMedia.objects.create(
#                    name='facebook',
#                    username=form_kwargs['data'].get('facebook'),
#                    profile_url='http://www.facebook.com/%s' % form_kwargs['data'].get('facebook'))
#                self.object.social_media.add(facebook)
#
#            # Add relation to Twitter
#            if form_kwargs['data'].get('twitter'):
#                username = form_kwargs['data'].get('twitter')
#                if username[:1] == '@':
#                    username = username[1:]
#                twitter = SocialMedia.objects.create(
#                    name='twitter',
#                    username=username,
#                    profile_url='http://twitter.com/%s' % form_kwargs['data'].get('twitter'))
#                self.object.social_media.add(twitter)
#
#            # Add relation to LinkedIn
#            if form_kwargs['data'].get('linkedin'):
#                linkedin = SocialMedia.objects.create(
#                    name='linkedin',
#                    profile_url=form_kwargs['data'].get('linkedin'))
#                self.object.social_media.add(linkedin)

            # Show save message
            messages.success(self.request, _('%s (Account) has been saved.') % self.object.name);

        return self.get_success_url()

    def form_invalid(self, form):
        """
        Overloading super().form_invalid to return a different response to ajax requests. For normal
        request: mark the primary checkbox as checked for postbacks.
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

        return super(AddAccountView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs = super(AddAccountView, self).get_context_data(**kwargs)

        # Add formsets to context for the normal form
        if not is_ajax(self.request):
            kwargs.update({
                'websites_formset': self.websites_formset,
                'email_addresses_formset': self.email_addresses_formset,
                'addresses_formset': self.addresses_formset,
                'phone_numbers_formset': self.phone_numbers_formset,
                'countries': COUNTRIES,
            })
        return kwargs

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return redirect('%s?order_by=4&sort_order=desc' % (reverse('account_list')))


class EditAccountView(UpdateView):
    """
    View to edit an acccount with all fields included in the template including support to add
    multiple instances of many-to-many relations with custom formsets.
    """
    template_name = 'accounts/create_or_update.html'
    form_class = EditAccountForm
    model = Account

    # Create formsets
    WebsiteFormSet = modelformset_factory(Website, form=WebsiteBaseForm, can_delete=True, extra=0)
    EmailAddressFormSet = modelformset_factory(EmailAddress, form=EmailAddressBaseForm, can_delete=True, extra=0)
    AddressFormSet = modelformset_factory(Address, form=AccountAddressForm, can_delete=True, extra=0)
    PhoneNumberFormSet = modelformset_factory(PhoneNumber, form=PhoneNumberBaseForm, can_delete=True, extra=0)

    def post(self, request, *args, **kwargs):
        """
        Overloading super().post to filter http:// as non provided value for the website field.
        Drawback: http:// dissappears from the input fields on postbacks.
        """
        post_data = request.POST.copy()
        if post_data.get('primary_website') and post_data['primary_website'] == 'http://':
            post_data['primary_website'] = ''

        request.POST = post_data

        return super(EditAccountView, self).post(request, *args, **kwargs)

    def get_form(self, form_class):
        """
        Overloading super().get_form to instantiate formsets while instantiating the form.
        """
        form = super(EditAccountView, self).get_form(form_class)

        self.websites_formset = form.websites_formset = self.WebsiteFormSet(self.request.POST or None, queryset=Website.objects.filter(account=self.object, is_primary=False), prefix='websites')
        self.email_addresses_formset = form.email_addresses_formset = self.EmailAddressFormSet(self.request.POST or None, queryset=self.object.email_addresses.all(), prefix='email_addresses')
        self.addresses_formset = form.addresses_formset = self.AddressFormSet(self.request.POST or None,  queryset=self.object.addresses.all(), prefix='addresses')
        self.phone_numbers_formset = form.phone_numbers_formset = self.PhoneNumberFormSet(self.request.POST or None,  queryset=self.object.phone_numbers.all(), prefix='phone_numbers')

        return form

    def form_valid(self, form):
        """
        Save m2m relations to edited account (i.e. Social media, Phone numbers,
        E-mail addresses and Addresses).
        """
        # Save instance
        super(EditAccountView, self).form_valid(form)

        form_kwargs = self.get_form_kwargs()

        # Save all e-mail address, phone number and address formsets
        if self.websites_formset.is_valid() and self.email_addresses_formset.is_valid() and self.addresses_formset.is_valid() and self.phone_numbers_formset.is_valid():
            # Handle websites
            for formset in self.websites_formset:
                # Check if existing instance has been marked for deletion
                if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                    formset.instance.delete()
                    continue
                # Only save website if more than initial was filled in
                if formset.instance.website and not formset.instance.website == formset.fields['website'].initial:
                    formset.instance.account = self.object
                    formset.save()

            # Handle e-mail addresses
            for formset in self.email_addresses_formset:
                # Check if existing instance has been marked for deletion
                if form_kwargs['data'].get(formset.prefix + '-DELETE'):
                    self.object.email_addresses.remove(formset.instance)
                    formset.instance.delete()
                    continue

                # Check for e-mail address selected as primary
                primary = form_kwargs['data'].get(self.email_addresses_formset.prefix + '_primary-email')
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

        # Add primary website
        if form_kwargs['data'].get('primary_website'):
            try:
                website = self.object.websites.get(is_primary=True)
                website.website = form_kwargs['data'].get('primary_website')
                website.save()
            except Website.DoesNotExist:
                Website.objects.create(account=self.object, is_primary=True,
                                       website = form_kwargs['data'].get('primary_website'))
        else:
            # Remove possible primary website
            try:
                website = Website.objects.filter(account=self.object, is_primary=True)
                website.delete()
            except Exception:
                pass

#        # Add relation to Facebook
#        if form_kwargs['data'].get('facebook'):
#            # Prevent re-creating
#            facebook, created = SocialMedia.objects.get_or_create(
#                name='facebook',
#                username=form_kwargs['data'].get('facebook'),
#                profile_url='http://www.facebook.com/%s' % form_kwargs['data'].get('facebook'))
#            if created:
#                self.object.social_media.add(facebook)
#        else:
#            # Remove possible Facebook relations
#            self.object.social_media.filter(name='facebook').delete()
#
#        # Add relation to Twitter
#        if form_kwargs['data'].get('twitter'):
#            # Prevent re-creating
#            username = form_kwargs['data'].get('twitter')
#            if username[:1] == '@':
#                username = username[1:]
#            twitter, created = SocialMedia.objects.get_or_create(
#                name='twitter',
#                username=username,
#                profile_url='http://twitter.com/%s' % form_kwargs['data'].get('twitter'))
#            if created:
#                self.object.social_media.add(twitter)
#        else:
#            # Remove possible Twitter relations
#            self.object.social_media.filter(name='twitter').delete()
#
#        # Add relation to LinkedIn
#        if form_kwargs['data'].get('linkedin'):
#            # Prevent re-creating
#            linkedin, created = SocialMedia.objects.get_or_create(
#                name='linkedin',
#                profile_url=form_kwargs['data'].get('linkedin'))
#            if created:
#                self.object.social_media.add(linkedin)
#        else:
#            # Remove possible LinkedIn relations
#            self.object.social_media.filter(name='linkedin').delete()

        # Show save message
        messages.success(self.request, _('%s (Account) has been edited.') % self.object.name);

        return self.get_success_url()

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add formsets for template.
        """
        kwargs = super(EditAccountView, self).get_context_data(**kwargs)
        kwargs.update({
            'websites_formset': self.websites_formset,
            'email_addresses_formset': self.email_addresses_formset,
            'addresses_formset': self.addresses_formset,
            'phone_numbers_formset': self.phone_numbers_formset,
            'countries': COUNTRIES,
        })
        return kwargs

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        # TODO: determine whether to go back to the list in search mode
        return redirect('%s?order_by=5&sort_order=desc' % (reverse('account_list')))


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
        messages.success(self.request, _('%s (Account) has been deleted.') % self.object.name);

        self.object.delete()

        # TODO: check for contacts ..

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
            edit_url = reverse('account_edit', kwargs={ 'pk': account.pk })
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