from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def handle(self, **options):
        """
        Wrapper around default django makemessages command to call it with better defaults.
        """

        arguments = options

        if not arguments.get('no_location', False):
            arguments['no_location'] = True

        if not arguments.get('all', False) and not arguments.get('locale', None):
            arguments['all'] = True

        super(Command, self).handle(**arguments)
