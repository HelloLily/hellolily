"""
Enable autostrip for input on all forms.
"""

import inspect, sys

from django.conf import settings
from django.forms.forms import BaseForm

from lily.utils.functions import autostrip


local_installed_apps = filter(lambda item: item.startswith('%s.' % __name__), settings.INSTALLED_APPS)

def is_form(member):
    """
    Allow only custom made classes which are a subclass from BaseForm to pass.
    """
    if not inspect.isclass(member):
        return False
    
    if not issubclass(member, BaseForm):
        return False
    
    return member.__module__.startswith(__name__) 

for app in local_installed_apps:
    try:
        __import__('%s.forms' % app)
    except ImportError:
        continue
    else:
        forms_module = sys.modules['%s.forms' % app]
        form_classes = inspect.getmembers(forms_module, lambda member: is_form(member))
        for form in form_classes:
            # Wrap the reference to this form with an autostrip function that auto strips the input.
            form_class = autostrip(form[1])
            setattr(forms_module, form[0], form_class)