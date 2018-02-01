from django.apps import AppConfig


class EmailWrapperLibConfig(AppConfig):
    """
    This is the custom app configuration for the lily app.
    Custom startup code is defined here.
    """
    name = 'email_wrapper_lib'
    verbose_name = 'email_wrapper_lib'

    def ready(self):
        # Import the registry as it is registers all the providers and thus loads their models and stuff.
        from .providers import registry  # noqa
