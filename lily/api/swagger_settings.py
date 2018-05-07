from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema, PaginatorInspector


swagger_info = openapi.Info(
    title="Lily API",
    default_version="v1",
    description="The Lily API allows you to interact with a Lily account (only available when on the Professional plan). \
    The API is RESTful and uses JSON to transport information. You can use Lily's API to create objects such as \
    accounts, cases, contacts and deals. \
    This documentation is mainly a collection of endpoints which can be used to help you access the Lily API. \
    <br /> \
    <br /> \
    This API documentation will get you started with your first requests with our API. \
    Once on the Professional plan, you can create an API token on the \
    [My API token](https://app.hellolily.com/#/preferences/user/token) page and get started right away. \
    ",
    contact=openapi.Contact(email="lily@hellolily.com"),
    license=openapi.License(name="AGPLv3"),
)


class LilyAutoSchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys):
        operation_id = super(LilyAutoSchema, self).get_operation_id(operation_keys)
        # Upper case first letter.
        operation_id = operation_id[0].upper() + operation_id[1:]
        # Remove underscores.
        operation_id = operation_id.replace('_', ' ')
        return operation_id


class CustomPaginationInspector(PaginatorInspector):
    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, 'Array return expected for paged response'

        paged_schema = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ('pagination', openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=OrderedDict((
                        ('total', openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Total number of items for the resource.',
                        )),
                        ('page_size', openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Number of items per page.',
                        )),
                        ('number_of_pages', openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Total number of pages for the endpoint.',
                        )),
                        ('current_page', openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Number of the current page of the endpoint.',
                        )),
                        ('next_page', openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_URI,
                            description='Link to the next page of the endpoint',
                        )),
                        ('prev_page', openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_URI,
                            description='Link to the previous page of the endpoint.',
                        )),
                    )),
                )),
                ('results', response_schema),
            )),
        )

        return paged_schema
