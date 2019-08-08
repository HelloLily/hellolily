import csv
import StringIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.deals.models import Deal
from lily.hubspot.prefetch_objects import tags_prefetch
from lily.hubspot.utils import _s
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


field_names = (
    'deal_id',
    'name',
    'description',
    'currency',
    'amount_once',
    'amount_recurring',
    'closed_date',
    'quote_id',
    'next_step_date',

    # Voys only fields
    'new_business',
    'is_checked',
    'twitter_checked',
    'card_sent',

    'owner',  # assigned_to
    'created_by',

    'status',
    'found_through',
    'contacted_by',
    'next_step',
    'why_customer',
    'why_lost',
    'newly_assigned',

    'account_id',
    'contact_id',

    # 'tags',  # TODO: check out tags
    'pandadoc_urls',

    'lily_created',
    'lily_modified',
)


class Command(BaseCommand):
    help = 'Export deals for specified tenant id.'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with deals export')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        deal_qs = Deal.objects.filter(
            is_deleted=False
        ).prefetch_related(
            tags_prefetch
        ).order_by('pk')
        paginator = Paginator(deal_qs, 100)

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            deal_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for deal in deal_list:
                data = {
                    'deal_id': _s(deal.pk),

                    'account_id': _s(deal.account_id),
                    'contact_id': _s(deal.contact_id),

                    'lily_created': _s(deal.created.strftime("%d %b %Y - %H:%M:%S")),
                    'lily_modified': _s(deal.modified.strftime("%d %b %Y - %H:%M:%S")),
                }
                writer.writerow(data)

        filename = 'exports/tenant_{}/deals.csv'.format(tenant_id)
        default_storage.save(name=filename, content=csvfile)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported deals. \n\n')
