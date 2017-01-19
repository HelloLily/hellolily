import traceback

from django.core.management.commands import migrate


class Command(migrate.Command):
    def handle(self, *args, **options):
        """
        Wrapper around default django migrate command to print a default message on error.
        """
        try:
            super(Command, self).handle(*args, **options)
        except Exception:
            traceback.print_exc()
            self.stderr.write('\nMigration error.\n')
