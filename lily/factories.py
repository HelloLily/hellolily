"""
Collect all factories from Lily apps in this module for easy access.

Instead of:
    from lily.cases.factories import CaseFactory
    from lily.contacts.factories import ContactFactory

You can use:
    from lily import factories
    factories.CaseFactory
    factories.ContactFactory
"""
import sys
import inspect

import factory
from django.conf import settings


def _is_factory(member):
    """
    Test if a member from a module is a Factory-based class and belongs to this
    project.

    Args:
        member(any): Any member of a class.

    Returns:
        bool: True if class member is a Factory class.
    """
    return (inspect.isclass(member) and issubclass(member, factory.Factory) and member.__module__.startswith('lily.'))


project_apps = [app for app in settings.INSTALLED_APPS if app.startswith('lily.')]
for app in project_apps:
    factories_name = '%s.factories' % app
    try:
        __import__(factories_name)
    except ImportError, e:
        # If the importerror is the following, it means there is no
        # module named factories in this module. We can skip this as
        # it is to be expected. Any other errors should be raised.
        if str(e) != 'No module named factories':
            raise e
    else:
        # Can't use the return value of __import__ since it returns the
        # top-level package. Fetch the subpackage from sys.modules
        # directly.
        factories_module = sys.modules[factories_name]
        factory_classes = inspect.getmembers(factories_module, lambda member: _is_factory(member))
        for factory_name, factory_class in factory_classes:
            setattr(sys.modules['lily.factories'], factory_name, factory_class)
