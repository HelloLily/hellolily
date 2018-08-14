import time

from django.core.management.base import BaseCommand

from lily.deals.models import Deal
from lily.tenant.models import Tenant


class Command(BaseCommand):
    help = """Remove all deals imported with specific "imported from" marker."""

    def add_arguments(self, parser):
        parser.add_argument('--tenant', dest='tenant', action='store', default='', help='Specify a tenant.')
        parser.add_argument(
            '--imported-from',
            dest='imported_from',
            action='store',
            default='',
            help='Specify an imported_from value.'
        )

    def handle(self, *args, **options):
        tenantOption = options.get('tenant')
        if not tenantOption:
            raise Exception('Need tenant option.')
        self.tenant = Tenant.objects.get(pk=int(tenantOption.strip()))
        self.stdout.write('Using tenant %s' % self.tenant.id)

        self.imported_from = options.get('imported_from')
        if not self.imported_from:
            raise Exception('Need "imported from" option!')

        deals_to_remove = Deal.objects.filter(tenant=self.tenant, imported_from=self.imported_from)

        if deals_to_remove.count() > 0:
            self.stdout.write(
                'Deleting %s deals from tenant %s with tag %s in 10 sec'
                ', hit Ctrl+C to abort.' % (deals_to_remove.count(), self.tenant.id, self.imported_from)
            )
            time.sleep(10)
            deals_to_remove.delete()
        else:
            self.stdout.write('No deals found in tenant %s with tag %s' % (self.tenant.id, self.imported_from))
