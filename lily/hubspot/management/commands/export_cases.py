import csv
import StringIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.hubspot.prefetch_objects import tags_prefetch
from lily.hubspot.utils import _s, get_mappings
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


field_names = (
    'case_id',
    'account_id',
    'contact_id',

    'priority',
    'subject',
    'description',
    'category',
    'owner',

    'pipeline',
    'stage',

    'tags',

    'create_date',
    'lily_created',
    'lily_modified',
)


class Command(BaseCommand):
    help = 'Export cases for specified tenant id.'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with cases export')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())
        m = get_mappings(tenant_id)

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        case_qs = Case.objects.filter(
            is_deleted=False,
            is_archived=True,
        ).prefetch_related(
            tags_prefetch
        ).order_by('pk')
        paginator = Paginator(case_qs, 1000)

        # Prevent mention of deleted accounts/contacts, also prevent None values.
        deleted_accounts = [None, ] + list(Account.objects.filter(is_deleted=True).values_list('id', flat=True))
        deleted_contacts = [None, ] + list(Contact.objects.filter(is_deleted=True).values_list('id', flat=True))

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            case_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for case in case_list:

                data = {
                    'case_id': _s(case.pk),
                    'account_id': _s(case.account_id if case.account_id not in deleted_accounts else ''),
                    'contact_id': _s(case.contact_id if case.contact_id not in deleted_contacts else ''),

                    'priority': _s(m.case_priority_to_ticket_priority_mapping.get(case.priority)),
                    'subject': _s(case.subject),
                    'description': _s(case.description),
                    'category': _s(m.case_type_to_ticket_category_mapping.get(case.type_id)),
                    'owner': _s(m.lilyuser_to_owner_mapping.get(case.assigned_to_id, '')),

                    'pipeline': _s(m.case_pipeline),
                    'stage': _s(m.case_status_to_ticket_stage_mapping.get(case.status_id, '')),

                    'tags': _s(','.join([tag.name for tag in case.prefetched_tags])),

                    'create_date': _s(case.created.strftime("%d/%m/%Y")),  # Tickets support native create date import.
                    'lily_created': _s(case.created.strftime("%d %b %Y - %H:%M:%S")),
                    'lily_modified': _s(case.modified.strftime("%d %b %Y - %H:%M:%S")),
                }
                writer.writerow(data)

        filename = 'exports/tenant_{}/cases.csv'.format(tenant_id)
        default_storage.save(name=filename, content=csvfile)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported cases. \n\n')
