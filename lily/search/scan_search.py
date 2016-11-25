import inspect

from django.conf import settings
from elasticutils.contrib.django import MappingType

from lily.search.base_mapping import BaseMapping


class ModelMappings(object):
    mappings = []
    model_to_mappings = {}
    app_to_mappings = {}

    @classmethod
    def scan(cls, apps_to_scan=settings.INSTALLED_APPS):
        mappings = []
        apps = []
        models = []

        for app in apps_to_scan:
            # Try because not every app has a search.py.
            try:
                # Import the child module 'search', hence the additional
                # parameters. (Otherwise only the top module is returned).
                search_module = __import__('%s.search' % app, globals(), locals(), ['search'])
                for name_member in inspect.getmembers(search_module, inspect.isclass):
                    member = name_member[1]
                    # Check if we defined a mapping class. We shall exclude
                    # members of BaseMapping or MappingType itself.
                    if issubclass(member, MappingType) and member is not BaseMapping and member is not MappingType:
                        cls.mappings.append(member)
                        cls.model_to_mappings[member.get_model()] = member
                        cls.app_to_mappings[app] = member
            except Exception:
                pass
