from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = 100  # The default page size.
    page_size_query_param = 'page_size'  # The query param used to custom define a page size per request.
    max_page_size = 200  # The hard limit for page size.

    def get_paginated_response(self, data):
        return Response(
            OrderedDict([
                (
                    'pagination',
                    OrderedDict([
                        ('total', self.page.paginator.count),  # Total number of objects, not only current page.
                        ('page_size', self.get_page_size(self.request)),  # The current page size used.
                        ('number_of_pages', self.page.paginator.num_pages),  # The total number of pages available.
                        ('current_page', self.page.number),  # The current page number.
                        ('next_page', self.get_next_link()),  # The link tot the next page.
                        ('prev_page', self.get_previous_link()),  # The link to the previous page.
                    ])
                ),
                ('results', data),  # Object list with all objects on the current page.
            ])
        )
