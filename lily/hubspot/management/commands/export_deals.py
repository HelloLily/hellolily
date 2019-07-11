from django.core.management.base import BaseCommand

from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


class Command(BaseCommand):
    help = 'Export deals for specified tenant id.'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with deals export')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())
