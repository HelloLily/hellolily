import operator
from datetime import datetime

import anyjson
import unicodecsv
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.db.models.loading import get_model
from django.forms.models import modelformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template import Context
from django.template.loader import get_template
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str
from django.utils.http import base36_to_int
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.edit import FormMixin, BaseCreateView, BaseUpdateView

from python_imap.folder import ALLMAIL
from lily.tags.models import Tag
from lily.accounts.forms import WebsiteBaseForm
from lily.accounts.models import Website
from lily.messaging.email.models import EmailAttachment
from lily.messaging.email.utils import get_attachment_filename_from_url
from lily.notes.views import NoteDetailViewMixin
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
            search_terms (list of strings): The strings that are used for searching.

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
                    partial_filter.append(Q(**{field: search_term}))
                # Combine the partial filter to one filter per search item, any of the fields should match
                complete_filter.append(reduce(operator.or_, partial_filter))
        # If there is no filter, don't apply filter
        if complete_filter:
            # Combine the filters to one filter, they must all match.
            queryset = queryset.filter(reduce(operator.and_, complete_filter)).distinct()
        return queryset


class DataTablesListView(FilterQuerysetMixin, ListView):
    """
    View that handles everything for server-side datatable processing.

    Subclass needs to set `columns`.

    Attributes:
        columns (list of dict): Subclass needs to set `columns` with an dictionary with all information needed for
            the setup of the Datatable columns. This must follow the aoColumns aoColumns parameter.
            See: https://datatables.net/usage/columns
        paginate_by (int): Initial view will load first 20 objects. TODO: make dynamic.
    """
    columns = []  # Dict setup like aoColumns
    paginate_by = 20
    _app_name = None

    def dispatch(self, request, *args, **kwargs):
        """
        # Check if it is an DataTables AJAX call and redirect request.
        """
        self.request = request
        self.args = args
        self.kwargs = kwargs

        # Get app_name from url.
        self._app_name = resolve(request.path).app_name

        if is_ajax(request) and request.GET.get('sEcho', False):
            return self.get_ajax(request)

        return super(DataTablesListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        It is not an DataTables AJAX call, setup pagination so that the resulting page will only
        show the first page before making Ajax request.
        """
        self.kwargs.update({
            'page': 1
        })
        return super(DataTablesListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Update the view to tell it needs to use DataTable on the serverside.
        """
        if not is_ajax(self.request):
            # If there are no search fields, we don't need to show any search field.
            show_search_field = 'false'
            if self.search_fields:
                show_search_field = 'true'
            # We add the extra info for the view to setup DataTables.
            kwargs.update({
                'data_tables_server_side': True,
                'data_tables_ajax_source': self.request.get_full_path,
                'data_tables_columns': self.get_data_tables_columns(),
                'data_tables_show_search_field': show_search_field,
                'columns': self.columns,
                'app_name': self._app_name,
            })
        return super(DataTablesListView, self).get_context_data(**kwargs)

    def get_ajax(self, request):
        """
        Handles the Ajax call from DataTable.

        Returns:
            HttpResponse: JSON parsed response.
        """
        # Get columns sent by DataTable.
        ajax_columns = self.get_columns(request.GET)

        # Get initial queryset.
        queryset = self.get_queryset()

        # DataTable needs to know how big the set is without filters.
        total_object_count = queryset.count()

        # Filter queryset.
        search_items = self.get_from_data_tables('search_items').split(' ')
        queryset = self.filter_queryset(queryset, search_items)
        filtered_object_count = queryset.count()

        # Order queryset.
        queryset = self.order_queryset(
            queryset,
            ajax_columns[int(self.get_from_data_tables('order_by'))],
            self.get_from_data_tables('sort_order')
        )

        # Paginate queryset.
        # NOTE In Django 1.4 you need to setup the page in the kwargs. (BOOH!)
        page_size = int(self.get_from_data_tables('page_size'))
        self.kwargs.update({
            'page': int(self.get_from_data_tables('page')) / page_size + 1
        })
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)

        # Parse data to columns for table.
        columns = self.parse_data_to_colums(queryset, ajax_columns)

        # Return json parsed response.
        return HttpResponse(anyjson.serialize({
            'iTotalRecords': total_object_count,
            'iTotalDisplayRecords': filtered_object_count,
            'sEcho': self.get_from_data_tables('echo'),
            'aaData': columns,
        }), mimetype='application/json')

    def get_columns(self, params):
        """
        Gets all columns from the ajax call and checks if it matches the columns in self.columns.

        Args:
            params (dict): The DataTables params sent by ajax request.

        Returns:
            list of dict: All matched columns.
        """
        ajax_columns = []
        x = 0
        while True:
            # Check if there is still a mDataProp left in params.
            param_name = 'mDataProp_%d' % x
            column_name = params.get(param_name, None)
            if column_name is None:
                break
            ajax_columns.append(column_name)
            x += 1
        return ajax_columns

    def get_from_data_tables(self, what, default=None):
        """
        Retrieve parameter from GET.

        Args:
            what (str): Parameter asked.
            default (optional): Default value if parameter doesn't exists.

        Returns:
            value from GET parameter.
        """
        return self.request.GET.get({
            'page_size': 'iDisplayLength',
            'echo': 'sEcho',
            'order_by': 'iSortCol_0',
            'sort_order': 'sSortDir_0',
            'search_items': 'sSearch',
            'page': 'iDisplayStart',
        }.get(what), default)

    def order_queryset(self, queryset, column, sort_order):
        """
        Orders the queryset.

        On default, no ordering will occur. This function needs to be implemented by a subclass.

        Args:
            queryset (QuerySet): QuerySet that needs to be ordered.
            column (str): Name of the column that needs ordering.
            sort_order (str): Always 'asc' or 'desc'.

        Returns:
            QuerySet: The ordered QuerySet.
        """
        return queryset

    def get_data_tables_columns(self):
        """
        Setup for the DataTable columns.

        Returns:
            json dict: A dictionary with all the columns and their properties.
        """
        if not self.columns:
            raise ImproperlyConfigured(
                'Need to setup columns attribute for DataTableListView to work'
            )
        return mark_safe(anyjson.serialize([value for value in self.columns.values()]))

    def parse_data_to_colums(self, object_list, columns):
        """
        Parses the queryset to the columns.

        Tries to render per column via a template, if there is no template found it will
        try to return an attribute on the object with the same name as the column.
        If both will not succeed, it will return an empty cell for the column.

        Args:
            object_list (QuerySet): The QuerySet with the objects needed to be parsed.
            columns (list): A list with columns needed in the result.

        Returns:
            list: A list with dictionaries.
        """
        parsed_data = []
        for item in object_list:
            row_data = {}
            for column in columns:
                # Load template for column.
                template = get_template('%s/data-tables/%s.html' % (self._app_name, column))
                response = template.render(Context({'item': item}))
                # Add response to row
                row_data[column] = response
            parsed_data.append(row_data)
        return parsed_data


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
            search_terms (list of strings): The strings that are used for searching.

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
                    partial_filter.append(Q(**{field: search_term}))
                # Combine the partial filter to one filter per search item, any of the fields should match
                complete_filter.append(reduce(operator.or_, partial_filter))
        # If there is no filter, don't apply filter
        if complete_filter:
            # Combine the filters to one filter, they must all match.
            queryset = queryset.filter(reduce(operator.and_, complete_filter)).distinct()
        return queryset


class DataTablesListView(FilterQuerysetMixin, ListView):
    """
    View that handles everything for server-side datatable processing.

    Subclass needs to set `columns`.

    Attributes:
        columns (list of dict): Subclass needs to set `columns` with an dictionary with all information needed for
            the setup of the Datatable columns. This must follow the aoColumns aoColumns parameter.
            See: https://datatables.net/usage/columns
        paginate_by (int): Initial view will load first 20 objects. TODO: make dynamic.
    """
    columns = []  # Dict setup like aoColumns
    paginate_by = 20
    _app_name = None

    def dispatch(self, request, *args, **kwargs):
        """
        # Check if it is an DataTables AJAX call and redirect request.
        """
        self.request = request
        self.args = args
        self.kwargs = kwargs

        # Get app_name from url.
        self._app_name = resolve(request.path).app_name

        if is_ajax(request) and request.GET.get('sEcho', False):
            return self.get_ajax(request)

        return super(DataTablesListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        It is not an DataTables AJAX call, setup pagination so that the resulting page will only
        show the first page before making Ajax request.
        """
        self.kwargs.update({
            'page': 1
        })
        return super(DataTablesListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Update the view to tell it needs to use DataTable on the serverside.
        """
        if not is_ajax(self.request):
            # If there are no search fields, we don't need to show any search field.
            show_search_field = 'false'
            if self.search_fields:
                show_search_field = 'true'
            # We add the extra info for the view to setup DataTables.
            kwargs.update({
                'data_tables_server_side': True,
                'data_tables_ajax_source': self.request.get_full_path,
                'data_tables_columns': self.get_data_tables_columns(),
                'data_tables_show_search_field': show_search_field,
                'columns': self.columns,
                'app_name': self._app_name,
            })
        return super(DataTablesListView, self).get_context_data(**kwargs)

    def get_ajax(self, request):
        """
        Handles the Ajax call from DataTable.

        Returns:
            HttpResponse: JSON parsed response.
        """
        # Get columns sent by DataTable.
        ajax_columns = self.get_columns(request.GET)

        # Get initial queryset.
        queryset = self.get_queryset()

        # DataTable needs to know how big the set is without filters.
        total_object_count = queryset.count()

        # Filter queryset.
        search_items = self.get_from_data_tables('search_items').split(' ')
        queryset = self.filter_queryset(queryset, search_items)
        filtered_object_count = queryset.count()

        # Order queryset.
        queryset = self.order_queryset(
            queryset,
            ajax_columns[int(self.get_from_data_tables('order_by'))],
            self.get_from_data_tables('sort_order')
        )

        # Paginate queryset.
        # NOTE In Django 1.4 you need to setup the page in the kwargs. (BOOH!)
        page_size = int(self.get_from_data_tables('page_size'))
        self.kwargs.update({
            'page': int(self.get_from_data_tables('page')) / page_size + 1
        })
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)

        # Parse data to columns for table.
        columns = self.parse_data_to_colums(queryset, ajax_columns)

        # Return json parsed response.
        return HttpResponse(anyjson.serialize({
            'iTotalRecords': total_object_count,
            'iTotalDisplayRecords': filtered_object_count,
            'sEcho': self.get_from_data_tables('echo'),
            'aaData': columns,
        }), mimetype='application/json')

    def get_columns(self, params):
        """
        Gets all columns from the ajax call and checks if it matches the columns in self.columns.

        Args:
            params (dict): The DataTables params sent by ajax request.

        Returns:
            list of dict: All matched columns.
        """
        ajax_columns = []
        x = 0
        while True:
            # Check if there is still a mDataProp left in params.
            param_name = 'mDataProp_%d' % x
            column_name = params.get(param_name, None)
            if column_name is None:
                break
            ajax_columns.append(column_name)
            x += 1
        return ajax_columns

    def get_from_data_tables(self, what, default=None):
        """
        Retrieve parameter from GET.

        Args:
            what (str): Parameter asked.
            default (optional): Default value if parameter doesn't exists.

        Returns:
            value from GET parameter.
        """
        return self.request.GET.get({
            'page_size': 'iDisplayLength',
            'echo': 'sEcho',
            'order_by': 'iSortCol_0',
            'sort_order': 'sSortDir_0',
            'search_items': 'sSearch',
            'page': 'iDisplayStart',
        }.get(what), default)

    def order_queryset(self, queryset, column, sort_order):
        """
        Orders the queryset.

        On default, no ordering will occur. This function needs to be implemented by a subclass.

        Args:
            queryset (QuerySet): QuerySet that needs to be ordered.
            column (str): Name of the column that needs ordering.
            sort_order (str): Always 'asc' or 'desc'.

        Returns:
            QuerySet: The ordered QuerySet.
        """
        return queryset

    def get_data_tables_columns(self):
        """
        Setup for the DataTable columns.

        Returns:
            json dict: A dictionary with all the columns and their properties.
        """
        if not self.columns:
            raise ImproperlyConfigured(
                'Need to setup columns attribute for DataTableListView to work'
            )
        return mark_safe(anyjson.serialize([value for value in self.columns.values()]))

    def parse_data_to_colums(self, object_list, columns):
        """
        Parses the queryset to the columns.

        Tries to render per column via a template, if there is no template found it will
        try to return an attribute on the object with the same name as the column.
        If both will not succeed, it will return an empty cell for the column.

        Args:
            object_list (QuerySet): The QuerySet with the objects needed to be parsed.
            columns (list): A list with columns needed in the result.

        Returns:
            list: A list with dictionaries.
        """
        parsed_data = []
        for item in object_list:
            row_data = {}
            for column in columns:
                # Load template for column.
                template = get_template('%s/data-tables/%s.html' % (self._app_name, column))
                response = template.render(Context({'item': item}))
                # Add response to row
                row_data[column] = response
            parsed_data.append(row_data)
        return parsed_data


#===================================================================================================
# Mixins
#===================================================================================================
class LoginRequiredMixin(object):
    """
    Use this mixin if you want that the view is only accessed when a user is logged in.

    This should be the first mixin as a superclass.
    """

    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


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
        search_terms = request.POST.get('export_filter', None).split(' ')
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
    """

    tag = None

    def get_queryset(self):
        """
        Overriding super().get_queryset to limit the queryset based on a kwarg when provided.
        """
        queryset = super(FilteredListByTagMixin, self).get_queryset()
        if queryset is not None:
            # if tag id is supplied, filter list on tagname
            if self.kwargs.get('tag', None):
                self.tag = get_object_or_404(Tag, pk=self.kwargs.get('tag'))
                content_type_of_model = ContentType.objects.get_for_model(self.model)
                tags = Tag.objects.filter(name=self.tag.name, content_type=content_type_of_model.pk)
                queryset = queryset.filter(pk__in=[tag.object_id for tag in tags])
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset'"
                                       % self.__class__.__name__)

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
        template = 'utils/formset_email_address.html'

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

            # Save e-mail address if an email address is filled in.
            if formset_form.instance.email_address:
                # Check if object already has a primary e-mail address.
                try:
                    self.object.email_addresses.get(is_primary=True)
                except EmailAddress.DoesNotExist:
                    # Make this the primary e-mail address.
                    formset_form.instance.is_primary = True

                # Save e-mail address and add to object.
                formset_form.save()
                self.object.email_addresses.add(formset_form.instance)

        return super(EmailAddressFormSetViewMixin, self).form_valid(form)


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
        template = 'utils/formset_phone_number.html'

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
        template = 'utils/formset_address.html'

        form_attrs = getattr(self, 'address_form_attrs', {})

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
        template = 'utils/formset_website.html'

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
        label = _('Files')
        template = 'utils/formset_attachment.html'

        self.add_formset(context_name, model=model, related_name=related_name, form=form, label=label, template=template, prefix=prefix)
        return super(AttachmentFormSetViewMixin, self).dispatch(request, *args, **kwargs)

    def get_attachments_queryset(self, instance):
        return EmailAttachment.objects.filter(message=self.object)

    def form_valid(self, form):
        context_name = 'attachments_formset'
        formset = self.get_formset(context_name)
        form_kwargs = self.get_form_kwargs()

        for formset_form in formset.forms:
            # Remove any unwanted (already existing) attachments
            if form_kwargs['data'].get(formset_form.prefix + '-DELETE'):
                if formset_form.instance.pk:
                    formset_form.instance.delete()
                else:
                    # Don't see a way to this properly: new attachments
                    # don't exist as formset_form.instances -> no primary key
                    # to compare to decide removal of an attachment, but
                    # this is something at the very least, so:
                    #                     #
                    # Clear attachments by filename
                    # Files in self.request.FILES have already been added to
                    # self.object.attachments. Check whether or not to 'cancel' attaching
                    # a file to self.object
                    for field_name, file_in_memory in self.request.FILES.items():
                        if field_name.startswith(formset_form.prefix):
                            for attachment in self.object.attachments.all():
                                if get_attachment_filename_from_url(attachment.attachment.name) == file_in_memory.name:
                                    attachment.delete()

            elif formset_form.instance.attachment:
                # Establish a link to a new message instance
                formset_form.instance.message = self.object
                formset_form.instance.save()

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
        return HttpResponse(anyjson.serialize({}), content_type='application/json')


class NotificationsView(TemplateView):
    """
    Renders template with javascript to show messages from django.contrib.
    messages as notifications.
    """
    http_method_names = ['get']
    template_name = 'utils/notifications.js'

    def get(self, request, *args, **kwargs):
        response = super(NotificationsView, self).get(request, *args, **kwargs)
        return HttpResponse(response.rendered_content, content_type='application/javascript')


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

            response = anyjson.serialize({
                'html': html,
                'show_more': response.context_data.get('show_more')
            })
            return HttpResponse(response, content_type='application/json')

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
notifications_view = NotificationsView.as_view()
