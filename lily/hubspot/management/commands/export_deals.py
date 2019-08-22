import csv
import StringIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.hubspot.mappings import lilyuser_to_owner_mapping, deal_status_to_status_mapping, \
    deal_found_through_to_found_us_through_mapping, deal_contacted_by_to_lead_source_mapping, \
    deal_why_customer_to_won_reason_mapping, deal_why_lost_to_lost_reason_mapping
from lily.hubspot.prefetch_objects import tags_prefetch
from lily.hubspot.utils import _s
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


field_names = (
    'deal_id',
    'name',
    'description',
    'amount',  # 'amount_once',
    'close_date',
    # 'next_step_date',  # Only archived deals to hubspot, so never a next step date.

    # Voys only fields
    # 'new_business',
    # 'is_checked',
    # 'twitter_checked',
    # 'card_sent',

    'owner',  # assigned_to

    'pipeline',  # This field is mandatory for hubspot and determines which statusses are available.
    'status',

    # 'original_source_type',  # 'found_through',  # This one for voys.
    'found_us_through',  # 'found_through',
    'lead_source',  # 'contacted_by',
    # 'next_step',
    'closed_won_reason',  # 'why_customer',
    'closed_lost_reason',  # 'why_lost',

    'account_id',
    'contact_id',

    # 'tags',
    # 'pandadoc_urls',

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

        # Prevent mention of deleted accounts/contacts, also prevent None values.
        deleted_accounts = [None, ] + list(Account.objects.filter(is_deleted=True).values_list('id', flat=True))
        deleted_contacts = [None, ] + list(Contact.objects.filter(is_deleted=True).values_list('id', flat=True))

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            deal_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for deal in deal_list:
                data = {
                    'deal_id': _s(deal.pk),
                    'name': _s(deal.name),
                    'description': _s(deal.description),
                    'amount': _s(deal.amount_once),
                    'close_date': _s(deal.closed_date.strftime("%d/%m/%Y") if deal.closed_date else ''),
                    'owner': _s(lilyuser_to_owner_mapping.get(deal.assigned_to_id, '')),
                    'pipeline': _s('New partners pipeline'),
                    'status': _s(deal_status_to_status_mapping.get(deal.status_id)),
                    'found_us_through': _s(deal_found_through_to_found_us_through_mapping.get(deal.found_through_id)),
                    'lead_source': _s(deal_contacted_by_to_lead_source_mapping.get(deal.contacted_by_id)),
                    'closed_won_reason': _s(deal_why_customer_to_won_reason_mapping.get(deal.why_customer_id, '')),
                    'closed_lost_reason': _s(deal_why_lost_to_lost_reason_mapping.get(deal.why_lost_id, '')),

                    'account_id': _s(deal.account_id if deal.account_id not in deleted_accounts else ''),
                    'contact_id': _s(deal.contact_id if deal.contact_id not in deleted_contacts else ''),

                    'lily_created': _s(deal.created.strftime("%d %b %Y - %H:%M:%S")),
                    'lily_modified': _s(deal.modified.strftime("%d %b %Y - %H:%M:%S")),
                }
                writer.writerow(data)

        filename = 'exports/tenant_{}/deals.csv'.format(tenant_id)
        default_storage.save(name=filename, content=csvfile)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported deals. \n\n')
