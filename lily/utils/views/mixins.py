import operator

from django.urls import reverse
from django.db.models import Q, FieldDoesNotExist
from django.http import HttpResponse
import unicodecsv


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
                    'columns_for_item':
                        ['columns_for_item',]  # Can be multiple columns, must match 'headers' in length.
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
            export_columns.insert(1, 'url')
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
            'form_action_url':
                reverse(
                    viewname=self.get_form_action_url_name(),
                    args=self.get_form_action_url_args(),
                    kwargs=self.get_form_action_url_kwargs(),
                ),
        })

        return context
