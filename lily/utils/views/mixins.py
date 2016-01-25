import operator
from collections import OrderedDict
from datetime import datetime

import anyjson
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, FieldDoesNotExist
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import base36_to_int
import unicodecsv

from lily.messaging.email.models.models import EmailMessage
from lily.notes.models import Note
from lily.notes.views import NoteDetailViewMixin
from lily.tags.models import Tag

from ..functions import is_ajax, combine_notes_qs_email_qs, get_emails_for_email_addresses


class LoginRequiredMixin(object):
    """
    Use this mixin if you want that the view is only accessed when a user is logged in.

    This should be the first mixin as a superclass.
    """

    @classmethod
    def as_view(cls, *args, **kwargs):
        return login_required(super(LoginRequiredMixin, cls).as_view(*args, **kwargs))


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
                    'columns_for_item': ['columns_for_item',]  # Can be multiple columns, must match 'headers' in length.
                },
            }
        search_fields (list of strings): The fields of the queryset where the queryset will be filtered on. The filter
            will match any object that has all the search strings on any of the fields of the object.
    """
    exportable_columns = {}
    search_fields = []
    file_name = 'export_list.csv'

    def get_items(self):
        # Get all items.
        queryset = self.get_queryset()

        # Filter items.
        search_terms = self.request.GET.get('export_filter', None)
        if search_terms:
            search_terms = set([term.lower() for term in search_terms.split(' ')])
            queryset = self.filter_queryset(queryset, search_terms)

        # Filter deleted items
        queryset = queryset.filter(is_deleted=False)

        return queryset.iterator()

    def value_for_column(self, item, column):
        return ''

    def get(self, request, *args, **kwargs):
        """
        """
        # Setup headers, columns and search
        headers = []
        columns = []
        export_columns = request.GET.getlist('export_columns', None)
        if export_columns:
            # Always insert id
            export_columns.insert(0, 'id')
            # There were columns in GET, check if they match self.exportable_columns.
            for column in export_columns:
                if self.exportable_columns.get(column, None):
                    headers.extend(self.exportable_columns[column].get('headers', []))
                    columns.extend(self.exportable_columns[column].get('columns_for_item', []))
        else:
            # Nothing in POST, we export every column set by view.
            for key, value in self.exportable_columns.iteritems():
                headers.extend(value.get('headers', []))
                columns.extend(value.get('columns_for_item', []))

        # Setup response type.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.file_name

        # Setup writer.
        writer = unicodecsv.writer(response)

        # Add headers to response.
        headers = [unicode(header) for header in headers]
        writer.writerow(headers)

        # For each item, make a row to export.
        for item in self.get_items():
            row = []
            for column in columns:
                # Get the value from the item.
                value = self.value_for_column(item, column)
                row.append(value)
            # Add complete row to response.
            writer.writerow(row)
        return response


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
        filtered_queryset = super(FilteredListByTagMixin, self).filter_queryset(queryset, search_terms)

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
            tags_queryset = queryset.filter(pk__in=[tag.object_id for tag in tags]).distinct()

            filtered_queryset = filtered_queryset | tags_queryset

        return filtered_queryset

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
    formset_classes = OrderedDict()
    formsets = OrderedDict()

    def __init__(self, *args, **kwargs):
        self.formset_data = {}
        self.formset_classes = OrderedDict()
        self.formsets = OrderedDict()

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
            if 'formsets' not in kwargs:
                kwargs['formsets'] = OrderedDict()

            for context_name, instance in self.formsets.items():
                kwargs['formsets'][context_name] = {
                    'instance': instance,
                    'label': self.formset_data[context_name]['label'],
                    'template': self.formset_data[context_name]['template']
                }

        return kwargs


class HistoryListViewMixin(NoteDetailViewMixin):
    # TODO: Can this class be removed?
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

    def get_notes_list(self, filter_date=None):
        """
        Build a Notes list for the current model.

        Arguments:
            filter_date (datetime): date before the message must be sent.

        Returns:
            A filtered Notes QuerySet.
        """
        model_content_type = ContentType.objects.get_for_model(self.model)

        # Build initial list with just notes.
        notes_list = Note.objects.filter(
            content_type=model_content_type,
            object_id=self.object.pk,
            is_deleted=False,
        ).order_by('-sort_by_date')

        # Filter on date if date is set
        if filter_date:
            notes_list = notes_list.filter(sort_by_date__lt=filter_date)

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

    def get_emails_list(self, filter_date=None):
        """
        Build an Email list for the current model.

        Returns:
            A filtered Notes QuerySet.
        """
        if hasattr(self, '_emails_list'):
            return self._emails_list

        # There always needs to be a QuerySet for email_list.
        email_list = EmailMessage.objects.none()

        # Build initial list with email messages if possible.
        email_address_list = self.get_related_email_addresses_for_object()
        if len(email_address_list) > 0:
            email_list = get_emails_for_email_addresses(
                email_address_list,
                self.request.user.tenant_id,
                self.page_size,
                filter_date,
            )

        setattr(self, '_emails_list', email_list)

        return email_list

    def get_notes_and_email_lists(self):
        """
        Build an Email and Notes list for the current model.

        Returns:
            A combined QuerySet with emails and notes.
        """

        # Filter lists by timestamp from request.GET.
        epoch = self.request.GET.get('datetime')
        filter_date = None
        if epoch:
            try:
                filter_date = datetime.fromtimestamp(int(epoch))
            except ValueError:
                pass

        notes_list = self.get_notes_list(filter_date)
        email_list = self.get_emails_list(filter_date)

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


class AjaxFormMixin(object):
    """
    Mixin to provide default functionality for ajax form views.
    """
    def form_valid(self, form):
        response = super(AjaxFormMixin, self).form_valid(form)

        if is_ajax(self.request):
            return self.form_ajax_valid(form, self.get_success_url())

        return response

    def form_ajax_valid(self, form, redirect_url):
        return HttpResponse(anyjson.serialize({
            'error': False,
            'redirect_url': redirect_url
        }), content_type='application/json')

    def form_invalid(self, form):
        """
        Overloading super().form_invalid to return a different response to ajax requests.
        """
        response = super(AjaxFormMixin, self).form_invalid(form)

        if is_ajax(self.request):
            return self.form_ajax_invalid(form, response.rendered_content)

        return response

    def form_ajax_invalid(self, form, html):
        return HttpResponse(anyjson.serialize({
            'error': True,
            'html': html,
        }), content_type='application/json')


class FormActionMixin(object):
    form_action_url_name = None
    form_action_url_args = None
    form_action_url_kwargs = None

    def get_form_action_url_name(self):
        return self.form_action_url_name or self.request.resolver_match.url_name

    def get_form_action_url_args(self):
        return self.form_action_url_args or {}

    def get_form_action_url_kwargs(self):
        return self.form_action_url_kwargs or {'pk': self.object.pk}

    def get_context_data(self, **kwargs):
        context = super(FormActionMixin, self).get_context_data(**kwargs)

        context.update({
            'form_action_url': reverse(
                viewname=self.get_form_action_url_name(),
                args=self.get_form_action_url_args(),
                kwargs=self.get_form_action_url_kwargs(),
            ),

        })

        return context
