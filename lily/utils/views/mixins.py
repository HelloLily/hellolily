import operator

from datetime import datetime

import anyjson
import unicodecsv

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q, FieldDoesNotExist
from django.forms.models import modelformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str
from django.utils.http import base36_to_int
from django.utils.translation import ugettext as _

from lily.messaging.email.models import EmailMessage
from lily.notes.models import Note
from lily.notes.views import NoteDetailViewMixin
from lily.utils.functions import is_ajax, combine_notes_qs_email_qs, get_emails_for_email_addresses
from lily.tags.models import Tag


class LoginRequiredMixin(object):
    """
    Use this mixin if you want that the view is only accessed when a user is logged in.

    This should be the first mixin as a superclass.
    """

    @classmethod
    def as_view(cls, *args, **kwargs):
        return login_required(super(LoginRequiredMixin, cls).as_view(*args, **kwargs))


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


class FilterQuerysetMixin(object):
    """
    Attributes:
        search_fields (list of str): The fields of the queryset where the queryset will be filtered on. The filter
            will match any object that has all the search strings on any of the fields of the object. If left empty,
            no search field will be rendered.
    """
    search_fields = []

    def filter_queryset(self, queryset, search_terms):
        """
        Filters the queryset given the search terms.

        The filter will match any object that has all the search strings on any of the fields of the object.
        Setup `search_fields` with strings of all the fieldnames you want to search on. For lookups that span
        relationships, use the Django default search arguments.

        Note: Lookups that span relationships with multiple search strings on siblings returns empty queryset.

        Args:
            queryset (QuerySet): QuerySet that needs to be filtered.
            search_terms (set of strings): The strings that are used for searching.

        Returns:
            QuerySet: The filtered Queryset
        """
        complete_filter = []
        # Loop through all the search items
        for search_term in search_terms:
            # Not searching for empty strings
            if search_term != '':
                partial_filter = []
                # For each field, lets build a partial filter
                for field in self.search_fields:
                    # Check if field needs to be searched with int.
                    try:
                        field_type = queryset.model._meta.get_field(field).get_internal_type()
                    except FieldDoesNotExist:
                        partial_filter.append(Q(**{field: search_term}))
                    else:
                        if field_type in ('AutoField', 'IntegerField'):
                            try:
                                partial_filter.append(Q(**{field: int(search_term)}))
                            except ValueError:
                                pass
                # Combine the partial filter to one filter per search item, any of the fields should match
                if partial_filter:
                    complete_filter.append(reduce(operator.or_, partial_filter))
        # If there is no filter, don't apply filter
        if complete_filter:
            # Combine the filters to one filter, they must all match.
            queryset = queryset.filter(reduce(operator.and_, complete_filter)).distinct()
        return queryset


class ExportListViewMixin(FilterQuerysetMixin):
    """
    Mixin that makes it possible to export current list view

    Post to view key 'export' with value what to export.
    Currently supported: csv.

    If `export_columns` in request.POST, only these will be exported.
    If `export_filter` in request.POST, object_list will be searched.

    Attributes:
        exportable_columns (dict): List with info on the columns to be exported. Should look like:
            exportable_columns = {
                'column_name_1': {
                    'headers': ['header_name_1',]  # Can be multiple columns.
                    'columns_for_item': ['columns_for_item',]  # Can be multple columns, must match 'headers' in length.
                },
            }
        search_fields (list of strings): The fields of the queryset where the queryset will be filtered on. The filter
            will match any object that has all the search strings on any of the fields of the object.
    """
    exportable_columns = []
    search_fields = []

    def post(self, request, *args, **kwargs):
        """
        Does a check if post has value of 'export' and handles export.
        """
        # Setup headers, columns and search
        headers = []
        columns = []
        export_columns = request.POST.get('export_columns[]', []).split(',')
        if export_columns:
            # There were columns in POST, check if they match self.exportable_columns.
            for column in export_columns:
                if self.exportable_columns.get(column):
                    headers.extend(self.exportable_columns[column].get('headers', []))
                    columns.extend(self.exportable_columns[column].get('columns_for_item', []))
        else:
            # Nothing in POST, we export every column set by view.
            for key, value in self.exportable_columns:
                headers.extend(value.get('headers', []))
                columns.extend(value.get('columns_for_item', []))

        # Find out what to export.
        export_type = request.POST.get('export', False)

        # Export csv.
        if export_type == 'csv':

            # Setup response type.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="export_list.csv"'

            # Setup writer.
            writer = unicodecsv.writer(response)

            # Add headers to response.
            writer.writerow(headers)

            # Get all items.
            queryset = self.get_queryset()

            # Filter items.
            search_terms = request.POST.get('export_filter', None).split(' ')
            search_terms = set([term.lower() for term in search_terms])
            queryset = self.filter_queryset(queryset, search_terms)

            # For each item, make a row to export.
            for item in queryset:
                row = []
                for column in columns:
                    # Get the value from the item.
                    value = getattr(self, 'value_for_column_%s' % column)(item)
                    if value is None:
                        value = ''
                    row.append(value)
                # Add complete row to response.
                writer.writerow(row)
            return response

        # nothing to export, this post is not for this view.
        return super(ExportListViewMixin, self).post(request, *args, **kwargs)


class FilteredListByTagMixin(object):
    """
    Mixin that enables filtering objects by tag, based on given tag kwarg

    Attributes:
        tags (instance): Tag model instance
    """

    tag = None
    _content_type_of_model = None

    def get_queryset(self):
        """
        Overriding super().get_queryset to limit the queryset based on a kwarg when provided.
        """
        queryset = super(FilteredListByTagMixin, self).get_queryset()
        if queryset is not None:
            # if tag id is supplied, filter list on tagname
            if self.kwargs.get('tag', None):
                self.tag = get_object_or_404(Tag, pk=self.kwargs.get('tag'))

                # Get Content Type of current model
                if not self._content_type_of_model:
                    self._content_type_of_model = ContentType.objects.get_for_model(self.model)

                tags = Tag.objects.filter(
                    name=self.tag.name,
                    content_type=self._content_type_of_model.pk
                ).values_list('object_id')

                queryset = queryset.filter(pk__in=[tag[0] for tag in tags])
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset'"
                                       % self.__class__.__name__)

        return queryset

    def filter_queryset(self, queryset, search_terms):
        """
        Filters the queryset given the search terms.

        The filter will match any object that has on of the search strings on any of the tags related to the object.
        Args:
            queryset (QuerySet): QuerySet that needs to be filtered.
            search_terms (set of strings): The strings that are used for searching.

        Returns:
            QuerySet: The filtered Queryset
        """
        complete_filter = []
        # Loop through all the search items
        for search_term in search_terms:
            # Not searching for empty strings
            if search_term != '':
                complete_filter.append(Q(**{'name__icontains': search_term}))

        # If there is no filter, don't apply filter
        if complete_filter:

            # Get Content Type of current model
            if not self._content_type_of_model:
                self._content_type_of_model = ContentType.objects.get_for_model(self.model)

            # Combine the filters to one filter, they must all match.
            tags = Tag.objects.filter(
                content_type=self._content_type_of_model
            ).filter(reduce(operator.or_, complete_filter)).distinct()
            queryset = queryset.filter(pk__in=[tag.object_id for tag in tags])

            # Remove matched tag names from further search
            search_terms = search_terms - set([tag.name.lower() for tag in tags])
        queryset = super(FilteredListByTagMixin, self).filter_queryset(queryset, search_terms)

        return queryset

    def get_context_data(self, **kwargs):
        """
        add extra context if there is a tag filter
        """
        kwargs = super(FilteredListByTagMixin, self).get_context_data(**kwargs)
        if self.tag:
            kwargs.update({
                'tag': self.tag
            })
        return kwargs


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
        kwargs = super(SortedListMixin, self).get_context_data(**kwargs)
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


class ModelFormSetViewMixin(object):
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


class HistoryListViewMixin(NoteDetailViewMixin):
    """
    Mix in a paginated list of history list items.
    Supports AJAX calls to show more older items.
    """
    page_size = 15

    def dispatch(self, request, *args, **kwargs):
        if is_ajax(request):
            self.template_name = 'utils/historylist.html'

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

            ajax_response = anyjson.serialize({
                'html': html,
                'show_more': response.context_data.get('show_more')
            })
            return HttpResponse(ajax_response, content_type='application/json')

        return response

    def get_notes_list(self):
        """
        Build a Notes list for the current model.

        Returns:
            A filtered Notes QuerySet.
        """
        model_content_type = ContentType.objects.get_for_model(self.model)

        # Build initial list with just notes.
        notes_list = Note.objects.filter(
            content_type=model_content_type,
            object_id=self.object.pk,
        ).order_by('-sort_by_date')

        return notes_list

    def get_related_email_addresses_for_object(self):
        """
        Check if object has attached email addresses and returns them.

        Returns:
            A Queryset of email addresses.
        """
        email_address_list = []
        if hasattr(self.object, 'email_addresses'):
            email_address_list = self.object.email_addresses.all()

        return email_address_list

    def get_emails_list(self):
        """
        Build an Email list for the current model.

        Returns:
            A filtered Notes QuerySet.
        """
        # There always needs to be a QuerySet for email_list.
        email_list = EmailMessage.objects.none()

        # Build initial list with email messages if possible.
        email_address_list = self.get_related_email_addresses_for_object()
        if len(email_address_list) > 0:
            email_list = get_emails_for_email_addresses(email_address_list)

        return email_list

    def get_notes_and_email_lists(self):
        """
        Build an Email and Notes list for the current model.

        Returns:
            A combined QuerySet with emails and notes.
        """

        notes_list = self.get_notes_list()
        email_list = self.get_emails_list()

        # Filter lists by timestamp from request.GET.
        epoch = self.request.GET.get('datetime')
        if epoch is not None:
            try:
                filter_date = datetime.fromtimestamp(int(epoch))
                notes_list = notes_list.filter(sort_by_date__lt=filter_date)
                email_list = email_list.filter(sort_by_date__lt=filter_date)
            except ValueError:
                pass

        # Paginate list.
        return combine_notes_qs_email_qs(notes_list, email_list, self.page_size)

    def get_context_data(self, **kwargs):
        """
        Build list of history items, i.e. notes/email messages.
        """
        kwargs = super(HistoryListViewMixin, self).get_context_data(**kwargs)

        # Get emails and notes
        object_list, show_more = self.get_notes_and_email_lists()

        kwargs.update({
            'object_list': object_list,
            'show_more': show_more,
        })

        return kwargs


class ArchivedFilterMixin(object):
    """
    Filter the list based on the `is_archived` attribute

    Attributes:
        show_archived (bool): Switch between only or non-archived objects.
    """
    show_archived = False

    def get_queryset(self):
        """
        Filters the queryset to only archived items or non-archived_items.
        """
        return super(ArchivedFilterMixin, self).get_queryset().filter(is_archived=self.show_archived)
