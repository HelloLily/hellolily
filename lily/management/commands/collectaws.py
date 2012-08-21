from django.core import management


class Command(management.base.NoArgsCommand):
    """
    Use mediagenerator to prepare static files for uploading to amazon s3.
    """
    def handle_noargs(self, **options):
        management.call_command('generatemedia', verbosity=0, interactive=False)
        management.call_command('uploadawsstatic', verbosity=0, interactive=False)
        