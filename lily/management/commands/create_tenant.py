from django.core.management.base import BaseCommand
from django.db import transaction
from lily.tenant.models import Tenant
from lily.tenant.utils import create_defaults_for_tenant


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            action='store',
            dest='tenant',
            default='',
            help='Specify a tenant to create the data for, or leave blank to manually set tenant info.'
        )

    def handle(self, **options):
        """
        Create a new tenant and fill it with sensible default values.
        """
        tenant_id = options['tenant']

        if tenant_id:
            tenant = Tenant.objects.get(pk=tenant_id)
        else:
            tenant_name = raw_input('Enter name for the new tenant: ')
            tenant_country = raw_input('Enter the country for the new tenant [NL]: ') or 'NL'

        with transaction.atomic():
            if not tenant:
                tenant = Tenant.create_tenant(name=tenant_name, country=tenant_country)

            create_defaults_for_tenant(tenant)

        print 'All done!'
