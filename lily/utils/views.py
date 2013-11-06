from datetime import date, datetime, timedelta
from hashlib import sha256
import base64
import operator
import pickle

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.loading import get_model
from django.forms.models import modelformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str
from django.utils.http import base36_to_int
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.edit import FormMixin, BaseCreateView, BaseUpdateView
from python_imap.folder import ALLMAIL
from templated_email import send_templated_mail

from lily.accounts.forms import WebsiteBaseForm
from lily.accounts.models import Website
from lily.messaging.email.models import EmailAttachment
from lily.notes.views import NoteDetailViewMixin
from lily.users.models import CustomUser
from lily.utils.forms import EmailAddressBaseForm, PhoneNumberBaseForm, AddressBaseForm, AttachmentBaseForm
from lily.utils.functions import is_ajax
from lily.utils.models import EmailAddress, PhoneNumber, Address, COUNTRIES, HistoryListItem


class CustomSingleObjectMixin(object):
    """
    Namespace the variables so this mixin can be combined with other
    mixins which also use model/queryset. Behaviour besides this is
    the same as default Django SingleObjectMixin.
    """
    detail_model = None
    detail_queryset = None
    detail_slug_field = 'slug'
    detail_context_object_name = None
    detail_slug_url_kwarg = 'slug'
    detail_pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.detail_queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom detail_queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_detail_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.detail_pk_url_kwarg, None)
        slug = self.kwargs.get(self.detail_slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_detail_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.detail_model._meta.verbose_name})
        return obj

    def get_detail_queryset(self):
        """
        Get the detail_queryset to look an object up against. May not be called if
        `get_object` is overridden.
        """
        if self.detail_queryset is None:
            if self.detail_model:
                return self.detail_model._default_manager.all()
            else:
                raise ImproperlyConfigured(u"%(cls)s is missing a detail_queryset. Define "
                                           u"%(cls)s.detail_model, %(cls)s.detail_queryset, or override "
                                           u"%(cls)s.get_object()." % {
                                               'cls': self.__class__.__name__
                                           })
        return self.detail_queryset._clone()

    def get_detail_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.detail_slug_field

    def get_detail_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.detail_context_object_name:
            return self.detail_context_object_name
        elif hasattr(obj, '_meta'):
            return smart_str(obj._meta.object_name.lower())
        else:
            return None


class CustomMultipleObjectMixin(object):
    """
    Namespace the variables so this mixin can be combined with other
    mixins which also use model/queryset. Behaviour besides this is
    the same as default Django MultipleObjectMixin.
    """
    allow_empty = True
    list_queryset = None
    list_model = None
    paginate_by = None
    list_context_object_name = None
    paginator_class = Paginator

    def get_list_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a list_queryset (in which qs-specific behavior will be enabled).
        """
        if self.list_queryset is not None:
            queryset = self.list_queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.list_model is not None:
            queryset = self.list_model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'list_queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the list_queryset, if needed.
        """
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_(u"Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            raise Http404(_(u'Invalid page (%(page_number)s)') % {
                'page_number': page_number
            })

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_list_context_object_name(self, object_list):
        """
        Get the name of the item to be used in the context.
        """
        if self.list_context_object_name:
            return self.list_context_object_name
        elif hasattr(object_list, 'model'):
            return smart_str('%s_list' % object_list.model._meta.object_name.lower())
        else:
            return None


class DetailListFormView(FormMixin, CustomSingleObjectMixin, CustomMultipleObjectMixin, TemplateResponseMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object_list = self.get_list_queryset()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        allow_empty = self.get_allow_empty()

        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})

        context = self.get_context_data(object=self.object, form=form, object_list=self.object_list)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object_list = self.get_list_queryset()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = kwargs

        detail_context_object_name = self.get_detail_context_object_name(self.object)
        if detail_context_object_name:
            context[detail_context_object_name] = self.object

        queryset = kwargs.pop('object_list')
        page_size = self.get_paginate_by(queryset)
        list_context_object_name = self.get_list_context_object_name(queryset)

        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context.update({
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            })
        else:
            context.update({
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            })

        if list_context_object_name is not None:
            context[list_context_object_name] = queryset

        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(object=self.object, form=form, object_list=self.object_list))


class MultipleModelListView(object):
    """
    Class for showing multiple lists of models in a template.
    """
    models = []  # Either a list of models or a dictionary
    object_lists = {}  # dictionary with all objects lists
    context_name_suffix = '_list'  # suffix for the context available in the template

    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to query for object lists first.
        """
        self.get_objects_lists()

        return super(MultipleModelListView, self).dispatch(request, *args, **kwargs)

    def get_objects_lists(self):
        """
        Retrieve the queryset for all models and save them in self.object_lists.
        """
        if isinstance(self.models, list):
            for model in self.models:
                list_name = smart_str(model._meta.object_name.lower())
                self.object_lists.update({
                    list_name: self.get_model_queryset(list_name, model)
                })
        elif isinstance(self.models, dict):
            for list_name, model in self.models.items():
                self.object_lists.update({
                    list_name: self.get_model_queryset(list_name, model)
                })

    def get_model_queryset(self, list_name, model):
        """
        Return the queryset for given model.
        """
        return model._default_manager.all()

    def get_context_data(self, **kwargs):
        """
        Put all object lists into the context data.
        """
        kwargs = super(MultipleModelListView, self).get_context_data(**kwargs)
        for list_name, object_list in self.object_lists.items():
            if isinstance(self.models, list):
                list_name = '%s%s' % (list_name, self.context_name_suffix)

            kwargs.update({
                list_name: object_list
            })
        return kwargs


#===================================================================================================
# Mixins
#===================================================================================================
class FilteredListMixin(object):
    """
    Mixin that enables filtering objects by url, based on their primary keys.
    """
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

        if hasattr(self, 'select_related'):
            queryset = queryset.select_related(*self.select_related)

        if hasattr(self, 'prefetch_related'):
            queryset = queryset.prefetch_related(*self.prefetch_related)

        return queryset


class SortedListMixin(object):
    """
    Mixin that enables sorting ascending and descending on set columns.
    """
    ASC = 'asc'
    DESC = 'desc'
    sortable = []  # Columns that can be ordered
    default_sort_order = ASC  # Direction to order in
    default_order_by = 1  # Column to order

    def __init__(self, *args, **kwargs):
        """
        Make sure default_order_by is in sortable or use the default regardless.
        """
        if hasattr(self, 'order_by') and self.order_by not in self.sortable:
            self.order_by = self.default_order_by

    def get_context_data(self, **kwargs):
        """
        Add sorting information from instance variables or request.GET.
        """

        try:
            if int(self.request.GET.get('order_by')) in self.sortable:
                self.order_by = self.request.GET.get('order_by')
            else:
                if not hasattr(self, 'order_by'):
                    self.order_by = self.default_order_by
        except:
            self.order_by = self.default_order_by

        if self.request.GET.get('sort_order') in [self.ASC, self.DESC]:
            self.sort_order = self.request.GET.get('sort_order')
        else:
            if not hasattr(self, 'sort_order'):
                self.sort_order = self.default_sort_order

        kwargs.update({
            'order_by': self.order_by,
            'sort_order': self.sort_order,
        })

        return kwargs


class DeleteBackAddSaveFormViewMixin(object):
    """
    Add support for four buttons with their respective intended form actions.
        delete
        back
        add or save
    """
    def post(self, request, *args, **kwargs):
        if not is_ajax(request):
            if request.POST.get('submit-delete', None):
                pass  # TODO: get delete url
            if request.POST.get('submit-back', None):
                success_url = self.get_success_url()  # TODO: ask if the user is sure to cancel when the form has been changed
                return redirect(success_url) if isinstance(success_url, basestring) else success_url
        # continue for other options (add or save)
        return super(DeleteBackAddSaveFormViewMixin, self).post(request, *args, **kwargs)


class ValidateFormSetViewMixin(object):
    """
    Mixin to include formsets when validating POST data.
    """
    def post(self, request, *args, **kwargs):
        if isinstance(self, BaseCreateView):
            # Copied from BaseCreateView.post()
            self.object = None
        elif isinstance(self, BaseUpdateView):
            # Copied from BaseUpdateView.post()
            self.object = self.get_object()

        # Copied from ProcessFormView to add formset validation
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        formset_is_valid = True
        if not is_ajax(self.request) and hasattr(self, 'formsets'):
            for name, formset in self.formsets.items():
                for formset_form in formset:
                    if not formset_form.is_valid():
                        formset_is_valid = False

        if formset_is_valid and form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class FormSetViewContextMixin(object):
    def get_form(self, form_class):
        """
        Pass formset instances to the FormHelper. It's a workaround to get these available in the
        context available to the TEMPLATE_PACK templates when rendered.
        """
        form = super(FormSetViewContextMixin, self).get_form(form_class)

        # Make all 'regular' context data available in crispy forms templates as well
        if hasattr(form, 'helper'):
            form.helper.__dict__.update(self.get_context_data())

        return form


class ModelFormSetViewMixin(FormSetViewContextMixin):
    """
    Mixin base class to add a formset to a FormView in an easier fashion.

    Create a new subclass with the following init method.
    def __init__(self, *args, **kwargs):
        context_name = 'context_name'
        model = Model
        related_name = 'related_name'
        form = Form
        label = 'label'
        template = 'template'
        prefix = 'prefix'
        extra = 0

        self.add_formset(context_name, model, related_name, form, label, template, prefix, extra)
        super(ModelFormSetViewMixinSubClass, self).__init__(*args, **kwargs)

    Custom queryset based on instances are possible using
    def get_%prefix%_queryset(self, instance):
        return instance.%related_name%.filter(filters)
    """
    formset_data = {}
    formset_classes = SortedDict()
    formsets = SortedDict()

    def __init__(self, *args, **kwargs):
        self.formset_data = {}
        self.formset_classes = SortedDict()
        self.formsets = SortedDict()

    def get_form(self, form_class):
        """
        Instantiate formsets for non-ajax requests.
        """
        form = super(ModelFormSetViewMixin, self).get_form(form_class)

        if not is_ajax(self.request):
            for context_name, formset_class in self.formset_classes.items():
                model = self.formset_data[context_name]['model']
                prefix = self.formset_data[context_name]['prefix']

                queryset = model._default_manager.none()
                if hasattr(self, 'get_%s_queryset' % prefix) and callable(getattr(self, 'get_%s_queryset' % prefix)):
                    queryset = getattr(self, 'get_%s_queryset' % prefix)(form.instance)
                else:
                    try:
                        queryset = getattr(form.instance, self.formset_data[context_name]['related_name']).all()
                    except:
                        pass

                formset_instance = formset_class(self.request.POST or None, queryset=queryset, prefix=prefix)

                self.add_formset_instance(context_name, formset_instance)

        return super(ModelFormSetViewMixin, self).get_form(form_class)

    def get_formset(self, context_name):
        """
        Return the formset instance for context_name.
        """
        return self.formsets.get(context_name, [])

    def add_formset(self, context_name, model, related_name, form, label, template, prefix, extra=0, **form_attrs):
        """
        Create a formset class for context_name.
        """
        if context_name in self.formset_data:
            # Update existing preset values
            self.formset_data[context_name] = dict({
                'model': model,
                'related_name': related_name,
                'form': form,
                'extra': extra,
                'label': label,
                'template': template,
                'prefix': prefix,
            }.items() + self.formset_data[context_name].items())
        else:
            self.formset_data.update({
                context_name: {
                    'model': model,
                    'related_name': related_name,
                    'form': form,
                    'extra': extra,
                    'label': label,
                    'template': template,
                    'prefix': prefix,
                }
            })

        for attr, value in form_attrs.items():
            setattr(form, attr, value)

        formset_class = modelformset_factory(model, form=form, can_delete=True, extra=extra)
        self.add_formset_class(context_name, formset_class)

    def add_formset_class(self, context_name, formset_class):
        """
        Set a formset class for context_name.
        """
        self.formset_classes.update({
            context_name: formset_class
        })

    def add_formset_instance(self, context_name, formset_instance):
        """
        Set a formset instance for context_name.
        """
        self.formsets[context_name] = formset_instance

    def get_context_data(self, **kwargs):
        """
        Pass all formsets to the context.
        """
        kwargs = super(ModelFormSetViewMixin, self).get_context_data(**kwargs)
        if not is_ajax(self.request):  # filter formsets from ajax requests
            if not 'formsets' in kwargs:
                kwargs['formsets'] = SortedDict()

            for context_name, instance in self.formsets.items():
                kwargs['formsets'][context_name] = {'instance': instance, 'label': self.formset_data[context_name]['label'], 'template': self.formset_data[context_name]['template']}

        return kwargs


class EmailAddressFormSetViewMixin(ModelFormSetViewMixin):
    """
    FormMixin for adding an e-mail address formset to a form.
    """
    def dispatch(self, request, *args, **kwargs):
        context_name = 'email_addresses_formset'
        model = EmailAddress
        related_name = 'email_addresses'
        form = EmailAddressBaseForm
        prefix = 'email_addresses'
        label = _('E-mail addresses')
        template = 'utils/mwsadmin/formset_email_address.html'

        self.add_formset(context_name, model=model, related_name=related_name, form=form, label=label, template=template, prefix=prefix)
        return super(EmailAddressFormSetViewMixin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        context_name = 'email_addresses_formset'
        formset = self.get_formset(context_name)

        form_kwargs = self.get_form_kwargs()
        for formset_form in formset:
            # Check if existing instance has been marked for deletion
            if form_kwargs['data'].get(formset_form.prefix + '-DELETE'):
                self.object.email_addresses.remove(formset_form.instance)
                if formset_form.instance.pk:
                    formset_form.instance.delete()
                continue

            # Check for e-mail address selected as primary
            primary = form_kwargs['data'].get(formset.prefix + '_primary-email')
            if formset_form.prefix == primary:
                formset_form.instance.is_primary = True
            else:
                formset_form.instance.is_primary = False

            # Save e-mail address if an email address is filled in
            if formset_form.instance.email_address:
                formset_form.save()
                self.object.email_addresses.add(formset_form.instance)

        return super(EmailAddressFormSetViewMixin, self).form_valid(form)

    def form_invalid(self, form):
        context_name = 'email_addresses_formset'
        formset = self.get_formset(context_name)

        form_kwargs = self.get_form_kwargs()
        primary = form_kwargs['data'].get(formset.prefix + '_primary-email')
        for formset_form in formset:
            if formset_form.prefix == primary:
                # Mark as selected
                formset_form.instance.is_primary = True

        return super(EmailAddressFormSetViewMixin, self).form_invalid(form)


class ValidateEmailAddressFormSetViewMixin(EmailAddressFormSetViewMixin):
    """
    FormMixin for adding an e-mail address formset to a form.
    Under certain conditions the user may need to validate an e-mail address
    before changes will be saved. It manages this by sending an e-mail to both e-mail addresses.
    """
    def form_valid(self, form):
        context_name = 'email_addresses_formset'
        formset = self.get_formset(context_name)

        # Check conditions for validating changed primary e-mail address
        form_kwargs = self.get_form_kwargs()

        # First, retrieve e-mail addresses.
        current_email_addresses = form.instance.email_addresses.all()
        posted_email_addresses = [formset_form.instance for formset_form in formset.forms]

        # Second, find out the which e-mail address is primary
        for formset_form in formset:
            # Check for e-mail address selected as primary
            primary = form_kwargs['data'].get(formset.prefix + '_primary-email')
            if formset_form.prefix == primary:
                formset_form.instance.is_primary = True
            else:
                formset_form.instance.is_primary = False

        linked_to_user = False  # If the contact is linked to a user
        allow_change = False  # Whether changes are allowed at all
        validate_on_change = False  # When changing primary e-mail address needs to be validated by e-mail
        send_validation_emails = False  # E-mails for confirming and saving primary e-mail change
        send_notification_email = False  # E-mails for notifying a user of his primary/login e-mail change

        # Third, check if the user is allowed to change e-mail addressess in the first place
        try:
            user = CustomUser.objects.get(contact=form.instance)
            linked_to_user = True
        except CustomUser.DoesNotExist:
            allow_change = True
        else:
            if user == self.request.user:  # User is allowed to change it's own address
                allow_change = True
                validate_on_change = True
            elif 'account_admin' in self.request.user.groups.values_list('name', flat=True):  # Users in this group can change other users e-mail addresses without validation
                allow_change = True

        # Fourth, check for primary e-mail addresses
        try:
            current_primary_email_address = current_email_addresses.get(is_primary=True)
        except:
            current_primary_email_address = None
        try:
            posted_primary_email_address = [email_address for email_address in posted_email_addresses if email_address.is_primary][0]
        except:
            posted_primary_email_address = None
        try:
            # Check if the primary e-mail address was deleted in the form, if there is a match, fake there is no posted primary e-mail address
            if posted_primary_email_address.email_address == [formset_form.instance for formset_form in formset.forms if form_kwargs['data'].get(formset_form.prefix + '-DELETE')][0].email_address:
                posted_primary_email_address = None
        except:
            pass

        # Check if the primary e-mail address was deleted (if there was any before)
        if linked_to_user and current_primary_email_address is not None and posted_primary_email_address is None:
            messages.error(self.request, _('The e-mail address %s was not removed because it\'s the login for this user.' % current_primary_email_address.email_address))
            allow_change = False
        # Check if the primary e-mail address was changed:
        elif linked_to_user and not None in [current_primary_email_address, posted_primary_email_address] and current_primary_email_address.email_address != posted_primary_email_address.email_address:
            if validate_on_change:
                send_validation_emails = True
            else:
                send_notification_email = True

        # Fifth, process information
        if allow_change:  # Changes are allowed at this time
            for formset_form in formset.forms:
                if form_kwargs['data'].get(formset_form.prefix + '-DELETE'):
                    # Delete primary e-mail address only for this contact when it's not linked to a user (deletes non-primary e-mail addresses regardless)
                    if not (linked_to_user and formset_form.instance.is_primary):
                        form.instance.email_addresses.remove(formset_form.instance)
                        if formset_form.instance.pk:
                            formset_form.instance.delete()
                # Save e-mail address if an address was provided
                elif formset_form.instance.email_address:
                    # Allow saving, when:
                    # - The e-mail address is not a primary e-mail address (old or new)
                    # - There is no need to send validation e-mails
                    # - The e-mail address is a primary e-mail address but hasn't changed.
                    if not (send_validation_emails and formset_form.instance.email_address in [current_primary_email_address.email_address, posted_primary_email_address.email_address]):
                        if not (send_validation_emails and formset_form.instance.is_primary and formset_form.instance.pk is not None and current_primary_email_address == posted_primary_email_address):
                            formset_form.save()
                            form.instance.email_addresses.add(formset_form.instance)
        else:  # Changes are not allowed
            pass

        if send_validation_emails:  # Changes will be made after validation
            # Get contact pk
            pk = self.object.pk

            # Calculate expire date
            expire_date = date.today() + timedelta(days=settings.EMAIL_CONFIRM_TIMEOUT_DAYS)
            expire_date_pickled = pickle.dumps(expire_date)

            # Get link to site
            protocol = self.request.is_secure() and 'https' or 'http'
            site = Site.objects.get_current()

            # Build data dict
            verification_email_data = base64.urlsafe_b64encode(pickle.dumps({
                'contact_pk': self.object.pk,
                'old_email_address': current_primary_email_address.email_address,
                'email_address': pickle.dumps(posted_primary_email_address),
                'expire_date': expire_date_pickled,
                'hash': sha256('%s%s%d%s' % (current_primary_email_address.email_address, posted_primary_email_address.email_address, pk, expire_date_pickled)).hexdigest(),
            })).strip('=')

            # Build verification link
            verification_link = "%s://%s%s" % (protocol, site, reverse('contact_confirm_email', kwargs={
                'data': verification_email_data
            }))

            # Send an e-mail asking the user to validate changing his primary e-mail address
            send_templated_mail(
                template_name='email_confirm',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[current_primary_email_address.email_address, posted_primary_email_address.email_address],
                context={
                    'current_site': site,
                    'full_name': self.object.full_name(),
                    'verification_link': verification_link,
                    'email_address': posted_primary_email_address.email_address,
                }
            )

            # Add message
            messages.info(self.request, _('An e-mail was sent to %s and %s with a link to verify your new primary e-mail address.' % (current_primary_email_address.email_address, posted_primary_email_address.email_address)))

        if allow_change and send_notification_email:  # Changes were made and the user will be notified on both e-mail addresses
            # Get link to site
            protocol = self.request.is_secure() and 'https' or 'http'
            site = Site.objects.get_current()

            # Send an e-mail informing the user his primary e-mail address has been changed.
            send_templated_mail(
                template_name='login_change',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[current_primary_email_address.email_address, posted_primary_email_address.email_address],
                context={
                    'current_site': site,
                    'full_name': self.object.full_name(),
                    'email_address': posted_primary_email_address.email_address,
                }
            )

        return super(ValidateEmailAddressFormSetViewMixin, self).form_valid(form)


class PhoneNumberFormSetViewMixin(ModelFormSetViewMixin):
    """
    FormMixin for adding a phone number formset to a form.
    """
    def dispatch(self, request, *args, **kwargs):
        context_name = 'phone_numbers_formset'
        model = PhoneNumber
        related_name = 'phone_numbers'
        form = PhoneNumberBaseForm
        prefix = 'phone_numbers'
        label = _('Phone numbers')
        template = 'utils/mwsadmin/formset_phone_number.html'

        self.add_formset(context_name, model=model, related_name=related_name, form=form, label=label, template=template, prefix=prefix)
        return super(PhoneNumberFormSetViewMixin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        context_name = 'phone_numbers_formset'
        formset = self.get_formset(context_name)

        form_kwargs = self.get_form_kwargs()
        for formset_form in formset:
            # Check if existing instance has been marked for deletion
            if form_kwargs['data'].get(formset_form.prefix + '-DELETE'):
                self.object.phone_numbers.remove(formset_form.instance)
                if formset_form.instance.pk:
                    formset_form.instance.delete()
                continue

            # Save number if raw_input is filled in
            if formset_form.instance.raw_input:
                formset_form.save()
                self.object.phone_numbers.add(formset_form.instance)

        return super(PhoneNumberFormSetViewMixin, self).form_valid(form)


class AddressFormSetViewMixin(ModelFormSetViewMixin):
    """
    FormMixin for adding an address formset to a form.
    """
    def dispatch(self, request, *args, **kwargs):
        context_name = 'addresses_formset'
        model = Address
        related_name = 'addresses'
        form = AddressBaseForm
        prefix = 'addresses'
        label = _('Addresses')
        template = 'utils/mwsadmin/formset_address.html'

        if hasattr(self, 'exclude_address_types'):
            form_attrs = {'exclude_address_types': self.exclude_address_types}

        self.add_formset(context_name, model=model, related_name=related_name, form=form, label=label, template=template, prefix=prefix, **form_attrs)
        return super(AddressFormSetViewMixin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        context_name = 'addresses_formset'
        formset = self.get_formset(context_name)

        form_kwargs = self.get_form_kwargs()
        for formset_form in formset:
            # Check if existing instance has been marked for deletion
            if form_kwargs['data'].get(formset_form.prefix + '-DELETE'):
                self.object.addresses.remove(formset_form.instance)
                if hasattr(formset, 'instance'):
                    if formset.instance.pk:
                        formset.instance.delete()
                continue

            # Save address if something else than complement or type is filled in
            if any([formset_form.instance.street,
                    formset_form.instance.street_number,
                    formset_form.instance.postal_code,
                    formset_form.instance.city,
                    formset_form.instance.state_province,
                    formset_form.instance.country]):
                formset_form.save()
                self.object.addresses.add(formset_form.instance)

        return super(AddressFormSetViewMixin, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to add a list of countries for address fields.
        """
        kwargs = super(AddressFormSetViewMixin, self).get_context_data(**kwargs)
        kwargs.update({
            'countries': COUNTRIES,
        })
        return kwargs


class WebsiteFormSetViewMixin(ModelFormSetViewMixin):
    """
    FormMixin for adding a website formset to a form.
    """
    def dispatch(self, request, *args, **kwargs):
        context_name = 'websites_formset'
        model = Website
        related_name = 'websites'
        form = WebsiteBaseForm
        prefix = 'websites'
        label = _('Websites')
        template = 'accounts/mwsadmin/formset_website.html'

        self.add_formset(context_name, model=model, related_name=related_name, form=form, label=label, template=template, prefix=prefix)
        return super(WebsiteFormSetViewMixin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        context_name = 'websites_formset'
        formset = self.get_formset(context_name)

        form_kwargs = self.get_form_kwargs()
        for formset_form in formset:
            # Check if existing instance has been marked for deletion
            if form_kwargs['data'].get(formset_form.prefix + '-DELETE'):
                if formset_form.instance.pk:
                    formset_form.instance.delete()
                continue

            # Save website if the initial value was overwritten
            if formset_form.instance.website and not formset_form.instance.website == formset_form.fields['website'].initial:
                formset_form.instance.account = self.object
                formset_form.save()

        return super(WebsiteFormSetViewMixin, self).form_valid(form)

    def get_websites_queryset(self, instance):
        return instance.websites.filter(is_primary=False)


class AttachmentFormSetViewMixin(ModelFormSetViewMixin):
    """
    FormMixin for adding an email attachment formset to a form.
    """
    def dispatch(self, request, *args, **kwargs):
        context_name = 'attachments_formset'
        model = EmailAttachment
        related_name = 'attachments'
        form = AttachmentBaseForm
        prefix = 'attachments'
        label = _('Attachments')
        template = 'utils/mwsadmin/formset_attachment.html'

        self.add_formset(context_name, model=model, related_name=related_name, form=form, label=label, template=template, prefix=prefix)
        return super(AttachmentFormSetViewMixin, self).dispatch(request, *args, **kwargs)

    def get_attachments_queryset(self, instance):
        return EmailAttachment.objects.filter(message_id=self.message_id)

    def form_valid(self, form):
        context_name = 'attachments_formset'
        formset = self.get_formset(context_name)

        form_kwargs = self.get_form_kwargs()
        for formset_form in formset:
            # Check if existing instance has been marked for deletion
            if form_kwargs['data'].get(formset_form.prefix + '-DELETE'):
                self.object.attachments.remove(formset_form.instance)
                if hasattr(formset, 'instance'):
                    if formset.instance.pk:
                        formset.instance.delete()
                continue

                formset_form.save()
                self.object.attachments.add(formset_form.instance)

        return super(AttachmentFormSetViewMixin, self).form_valid(form)


class AjaxUpdateView(View):
    """
    View that provides an option to update models based on a url and POST data.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            app_name = kwargs.pop('app_name')
            model_name = kwargs.pop('model_name').lower().capitalize()
            object_id = kwargs.pop('object_id')

            model = get_model(app_name, model_name)
            instance = model.objects.get(pk=object_id)

            changed = False
            for key, value in request.POST.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                    changed = True

            if changed:
                instance.save()
        except:
            raise Http404()

        # Return response
        return HttpResponse(simplejson.dumps({}), mimetype='application/json')


class NotificationsView(TemplateView):
    """
    Renders template with javascript to show messages from django.contrib.
    messages as notifications.
    """
    http_method_names = ['get']
    template_name = 'utils/notifications.js'

    def get(self, request, *args, **kwargs):
        response = super(NotificationsView, self).get(request, *args, **kwargs)
        return HttpResponse(response.rendered_content, mimetype='application/javascript')


class HistoryListViewMixin(NoteDetailViewMixin):
    """
    Mix in a paginated list of history list items.
    Supports AJAX calls to show more older items.
    """
    page_size = 15

    def dispatch(self, request, *args, **kwargs):
        if is_ajax(request):
            self.template_name = 'utils/history_list.html'

        return super(HistoryListViewMixin, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        For AJAX calls, reply with a JSON response.
        """
        response = super(HistoryListViewMixin, self).get(request, *args, **kwargs)

        if is_ajax(request):
            html = ''
            if len(response.context_data.get('object_list')) > 0:
                html = response.rendered_content

            response = simplejson.dumps({
                'html': html,
                'show_more': response.context_data.get('show_more')
            })
            return HttpResponse(response, mimetype='application/json')

        return response

    def get_context_data(self, **kwargs):
        """
        Build list of history items, i.e. notes/email messages.
        """
        kwargs = super(HistoryListViewMixin, self).get_context_data(**kwargs)
        note_content_type = ContentType.objects.get_for_model(self.model)

        # Build initial list with just notes
        object_list = HistoryListItem.objects.filter(
            (Q(note__content_type=note_content_type) & Q(note__object_id=self.object.pk))
        )

        # Expand list with email messages if possible
        if hasattr(self.object, 'email_addresses'):
            email_address_list = [x.email_address for x in self.object.email_addresses.all()]
            if len(email_address_list) > 0:
                filter_list = [Q(message__emailmessage__headers__value__contains=x) for x in email_address_list]
                object_list = object_list | HistoryListItem.objects.filter(
                    Q(message__emailmessage__folder_identifier=ALLMAIL) &
                    Q(message__emailmessage__headers__name__in=['To', 'From', 'CC', 'Delivered-To', 'Sender']) &
                    reduce(operator.or_, filter_list)
                )

        # Filter list by timestamp from request.GET
        epoch = self.request.GET.get('datetime')
        if epoch is not None:
            try:
                filter_date = datetime.fromtimestamp(int(epoch))
                object_list = object_list.filter(sort_by_date__lt=filter_date)
            except ValueError:
                pass

        # Paginate list
        object_list = object_list.distinct().order_by('-sort_by_date')
        kwargs.update({
            'object_list': object_list[:self.page_size],
            'show_more': len(object_list) > self.page_size
        })

        return kwargs


# Perform logic here instead of in urls.py
ajax_update_view = login_required(AjaxUpdateView.as_view())
notifications_view = login_required(NotificationsView.as_view())
