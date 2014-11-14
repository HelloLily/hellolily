from django.core import management
from django.core.management import CommandError
from django.core.management.commands import compilemessages


class Command(compilemessages.Command):
    def handle(self, **options):
        """
        Wrapper around default django compilemessages command to automatically call compilejsi18n afterwards.
        """
        super(Command, self).handle(**options)
        management.call_command('compilejsi18n')
