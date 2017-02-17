from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    help = """Log every user out by removing all the sessions from the database."""

    def handle(self, *args, **kwargs):
        self.stdout.write('Invalidating all sessions.')
        Session.objects.all().delete()
        self.stdout.write('Done.')
