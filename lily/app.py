import sys
import inspect

from django.apps import AppConfig
from django.conf import settings
from django.forms.forms import BaseForm

from lily.utils.functions import autostrip


class LilyConfig(AppConfig):
    """
    This is the custom app configuration for the lily app.
    Custom startup code is defined here.
    """
    name = 'lily'
    verbose_name = 'HelloLily'

    def is_form(self, member):
        """
        Allow only custom made classes which are a subclass from BaseForm to pass.
        """
        if not inspect.isclass(member):
            return False

        if not issubclass(member, BaseForm):
            return False

        return member.__module__.startswith(__name__)

    def ready(self):
        """
        Code run on startup of django.
        """
        # Patch all the forms to strip whitespace from field input
        local_installed_apps = [app for app in settings.INSTALLED_APPS if app.startswith('%s.' % __name__)]
        for app in local_installed_apps:
            try:
                __import__('%s.forms' % app)
            except ImportError:
                continue
            else:
                forms_module = sys.modules['%s.forms' % app]
                form_classes = inspect.getmembers(forms_module, lambda member: self.is_form(member))
                for form_name, form in form_classes:
                    # Wrap the reference to this form with a function that strips the input from whitespace.
                    if hasattr(form, 'base_fields'):
                        form_class = autostrip(form)
                        setattr(forms_module, form_name, form_class)
