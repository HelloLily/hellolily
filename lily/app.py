import sys
import inspect

import analytics
from ddtrace import patch_all
from django.apps import AppConfig
from django.conf import settings
from django.forms.forms import BaseForm

from ddtrace.contrib.boto.patch import patch as patch_boto
from ddtrace.contrib.elasticsearch.patch import patch as patch_elasticsearch
from ddtrace.contrib.redis.patch import patch as patch_redis
from ddtrace.contrib.requests.patch import patch as patch_requests

from lily.search.scan_search import ModelMappings
from lily.utils.functions import autostrip


class LilyConfig(AppConfig):
    """
    This is the custom app configuration for the lily app.
    Custom startup code is defined here.
    """
    name = 'lily'
    verbose_name = 'Lily'

    def ready(self):
        """
        Code run on startup of django.
        """
        patch_all()

        local_apps = [app for app in settings.INSTALLED_APPS if app.startswith('lily')]

        self.patch_forms(local_apps)
        self.scan_indexes(local_apps)
        self.import_signals(local_apps)

        # Setup Segment.
        analytics.write_key = settings.SEGMENT_PYTHON_SOURCE_WRITE_KEY
        analytics.debug = settings.DEBUG

        # Setup DataDog.
        if settings.DATADOG_ENABLED:
            patch_boto()
            patch_elasticsearch()
            patch_redis()
            patch_requests()

    def patch_forms(self, local_apps):
        """
        Patch all the forms to strip whitespaces from field input.
        """
        def is_form(member):
            """
            Allow only custom made classes which are a subclass from BaseForm to pass.
            """
            if not inspect.isclass(member):
                return False

            if not issubclass(member, BaseForm):
                return False

            return member.__module__.startswith(self.name)

        for app in local_apps:
            try:
                __import__('%s.forms' % app)
            except ImportError:
                continue
            else:
                forms_module = sys.modules['%s.forms' % app]
                form_classes = inspect.getmembers(forms_module, lambda member: is_form(member))

                for form_name, form in form_classes:
                    # Wrap the reference to this form with a function that strips the input from whitespace.
                    if hasattr(form, 'base_fields'):
                        form_class = autostrip(form)
                        setattr(forms_module, form_name, form_class)

    def scan_indexes(self, local_apps):
        """
        Scan the installed apps for indexes.
        """
        ModelMappings.scan(local_apps)

    def import_signals(self, local_apps):
        """
        Import signals for the local apps if available.
        """
        for app in local_apps:
            try:
                __import__('%s.signals' % app)
            except ImportError:
                continue
