import inspect

from django.conf import settings
from elasticutils.contrib.django import MappingType

from lily.search.base_mapping import BaseMapping


class ModelMappings:
    _cache_model_mappings = None

    @classmethod
    def get_model_mappings(cls):
        """
        Scans the installed applications for search mappings.

        Returns:
            Dict of 'model to model mapping' entries.
        """
        if not cls._cache_model_mappings:
            mappings = []
            for app in settings.INSTALLED_APPS:
                try:
                    # Import the child module 'search', hence the additional
                    # parameters. (Otherwise only the top module is returned).
                    search_module = __import__('%s.search' % app, globals(), locals(), ['search'])
                    for name_member in inspect.getmembers(search_module, inspect.isclass):
                        member = name_member[1]
                        # Check if we defined a mapping class. We shall exclude
                        # members of BaseMapping or MappingType itself.
                        if (issubclass(member, MappingType)
                                and member is not BaseMapping
                                and member is not MappingType):
                            mappings.append(member)
                except:
                    pass
            model_mappings = {kls.get_model(): kls for kls in mappings}
            # Cache the mappings.
            cls._cache_model_mappings = model_mappings
        return cls._cache_model_mappings
