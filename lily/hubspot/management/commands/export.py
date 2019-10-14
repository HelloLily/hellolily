from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with export. \n\n')

        call_command('export_accounts', tenant_id)
        call_command('export_contacts', tenant_id)
        call_command('export_cases', tenant_id)
        call_command('export_deals', tenant_id)
        call_command('export_notes', tenant_id)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported. \n\n')
