import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.db.models.loading import get_model
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.edit import FormMixin

from lily.utils.functions import is_ajax
from lily.utils.views.mixins import CustomSingleObjectMixin, CustomMultipleObjectMixin, FilterQuerysetMixin


class ArchiveView(View):
    """
    Abstract view that makes it possible to archive an item which redirects to success_url afterwards.

    Needs a post, with one or more ids[] for the instance to be archived.
    Subclass needs to set `success_url` or override `get_success_url`.
    """
    model = None
    queryset = None
    success_url = None  # Needs to be set in subclass, or override get_success_url.
    http_method_names = ['post']

    def get_object_pks(self):
        """
        Get primary key(s) from POST.

        Raises:
            AttributeError: If no object_pks can be retrieved.
        """
        object_pks = self.request.POST.get('ids[]', None)
        if not object_pks:
            # No objects posted.
            raise AttributeError(
                'Generic Archive view %s must be called with at least one object pk.'
                % self.__class__.__name__
            )
        # Always return as a list.
        return object_pks.split(',')

    def get_queryset(self):
        """
        Default function from MultipleObjectMixin.get_queryset, and slightly modified.

        Raises:
            ImproperlyConfigured: If there is no queryset or model set.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "'%s' must define 'queryset' or 'model'"
                % self.__class__.__name__
            )

        # Filter the queryset with the pk's posted.
        queryset = queryset.filter(pk__in=self.get_object_pks())

        return queryset

    def get_success_message(self, n):
        """
        Should be overridden if there needs to be a success message after archiving objects.

        Args:
            n (int): Number of objects that were affected by the action.
        """
        pass

    def get_success_url(self):
        """
        Returns the succes_url if set, otherwise will raise ImproperlyConfigured.

        Returns:
            the success_url.
        """
        self.success_url = self.request.POST.get('success_url', self.success_url)
        if self.success_url is None:
            raise ImproperlyConfigured(
                "'%s' must define a success_url" % self.__class__.__name__
            )
        return self.success_url

    def archive(self, archive=True):
        """
        Archives all objects found.

        Returns:
            HttpResponseRedirect object set to success_url.
        """
        queryset = self.get_queryset()
        queryset.update(is_archived=archive)
        self.get_success_message(len(queryset))

        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        """
        Catch post to start archive process.
        """
        return self.archive(archive=True)


class UnarchiveView(ArchiveView):
    """
    Abstract view that makes it possible to un-archive an item which redirects to success_url afterwards.

    Needs a post, with at least one pk for the instance to be archived.
    """
    def post(self, request, *args, **kwargs):
        """
        Catch post to start un-archive process.
        """
        return self.archive(archive=False)


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
        search_terms = self.get_from_data_tables('search_items').split(' ')
        search_terms = set([term.lower() for term in search_terms])
        queryset = self.filter_queryset(queryset, search_terms)
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
        return HttpResponse(json.dumps({
            'iTotalRecords': total_object_count,
            'iTotalDisplayRecords': filtered_object_count,
            'sEcho': self.get_from_data_tables('echo'),
            'aaData': columns,
        }), content_type='application/json')

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
        return mark_safe(json.dumps([value for value in self.columns.values()]))

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
        return HttpResponse(json.dumps({}), content_type='application/json')


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


class JsonListView(FilterQuerysetMixin, ListView):
    """
    Attributes:
        filter_on_field (str): The field of the queryset where the queryset will be filtered on.
    """
    filter_on_field = None

    # Total QuerySet count after filtering
    _total = 0

    def dispatch(self, request, *args, **kwargs):
        # Set pagination
        self.paginate_by = int(request.GET.get('page_limit', 10))
        return super(JsonListView, self).dispatch(request, *args, **kwargs)

    def order_queryset(self, queryset):
        """
        Set the ordering of the queryset

        Arguments:
            queryset (instance): QuerySet instance

        Returns:
            queryset (instance): ordered QuerySet instance
        """
        return queryset.order_by('-modified')

    def get_queryset(self):
        """
        Get a filtered and searched queryset.

        The QuerySet is filtered on given GET `q` and on given
        ``filter_on_related_object`` and GET `filter`.

        Sets ``count`` with number of results in QuerySet.

        Returns:
            queryset (instance): Filtered and searched QuerySet
        """
        queryset = super(JsonListView, self).get_queryset()

        # Filter on related object
        filter = self.request.GET.get('filter', None)
        if filter and self.filter_on_field:
            queryset = queryset.filter(Q(**{self.filter_on_field: filter}))

        # Search on queryset
        search_terms = self.request.GET.get('q', None).split(' ')
        if search_terms:
            queryset = self.filter_queryset(queryset, search_terms)

        queryset = self.order_queryset(queryset)
        self._total = queryset.count()
        return queryset

    def render_to_response(self, context, **response_kwargs):
        # Return json response with paginated object results and total queryset count.
        contacts = []
        for object in context['object_list']:
            contacts.append({'id': object.pk, 'text': str(object)})
        response = json.dumps({
            'objects': contacts,
            'total': self._total
        })
        return HttpResponse(response, content_type="application/javascript")


# Perform logic here instead of in urls.py
ajax_update_view = login_required(AjaxUpdateView.as_view())
notifications_view = NotificationsView.as_view()
