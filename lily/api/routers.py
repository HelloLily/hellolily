from rest_framework import routers


# Copyright 2013 Alan Justino da Silva, Oscar Vilaplana, et. al.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
class SimpleRouter(routers.SimpleRouter):
    """
    Improvement of rest_framework.routers.SimpleRouter that allows the
    lookup of urls of nested resources.
    """
    def get_lookup_regex(self, viewset, lookup_prefix=''):
        """
        Given a viewset, return the portion of URL regex that is used
        to match against a single instance.
        """
        base_regex = '(?P<{lookup_prefix}{lookup_field}>[^/]+)'
        lookup_field = getattr(viewset, 'lookup_field', 'pk')
        return base_regex.format(lookup_field=lookup_field, lookup_prefix=lookup_prefix)


class NestedSimpleRouter(SimpleRouter):
    def __init__(self, parent_router, parent_prefix, *args, **kwargs):
        self.parent_router = parent_router
        self.parent_prefix = parent_prefix
        self.nest_count = getattr(parent_router, 'nest_count', 0) + 1
        self.nest_prefix = kwargs.pop('lookup', 'nested_%i' % self.nest_count) + '_'
        super(NestedSimpleRouter, self).__init__(*args, **kwargs)

        parent_registry = [
            registered for registered in self.parent_router.registry if registered[0] == self.parent_prefix
        ]
        try:
            parent_registry = parent_registry[0]
            parent_prefix, parent_viewset, parent_basename = parent_registry
        except:
            raise RuntimeError('parent registered resource not found')

        nested_routes = []
        parent_lookup_regex = parent_router.get_lookup_regex(parent_viewset, self.nest_prefix)
        self.parent_regex = '{parent_prefix}/{parent_lookup_regex}/'.format(
            parent_prefix=parent_prefix,
            parent_lookup_regex=parent_lookup_regex
        )
        if hasattr(parent_router, 'parent_regex'):
            self.parent_regex = parent_router.parent_regex+self.parent_regex

        for route in self.routes:
            route_contents = route._asdict()

            route_contents['url'] = route.url.replace('^', '^'+self.parent_regex)
            nested_routes.append(type(route)(**route_contents))

        self.routes = nested_routes
