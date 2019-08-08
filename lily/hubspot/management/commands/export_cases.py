import csv
import StringIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.cases.models import Case
from lily.hubspot.mappings import lilyuser_to_owner_mapping, case_status_to_ticket_status_mapping, \
    case_type_to_ticket_category_mapping, case_priority_to_ticket_priority_mapping
from lily.hubspot.prefetch_objects import tags_prefetch
from lily.hubspot.utils import _s
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


field_names = (
    'case_id',
    'priority',
    'subject',
    'description',
    'status',
    'category',  # 'type',  # TODO: map type to category
    'owner',  # assigned_to
    'pipeline',  # TODO: which pipeline? -> level support 1

    'account_id',
    'contact_id',

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

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        case_qs = Case.objects.filter(
            is_deleted=False
        ).prefetch_related(
            tags_prefetch
        ).order_by('pk')
        paginator = Paginator(case_qs, 100)

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            case_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for case in case_list:

                if case.is_archived:
                    pipeline = 'Support archived'
                    status = 'Support archived'
                else:
                    pipeline = 'Level 1 support'
                    status = case_status_to_ticket_status_mapping.get(case.status_id)

                data = {
                    'case_id': _s(case.pk),
                    'priority': _s(case_priority_to_ticket_priority_mapping.get(case.priority)),
                    'subject': _s(case.subject),
                    'description': _s(case.description),
                    'status': _s(status),
                    'category': _s(case_type_to_ticket_category_mapping.get(case.type_id)),
                    'owner': _s(lilyuser_to_owner_mapping.get(case.assigned_to_id, '')),
                    'pipeline': pipeline,

                    'account_id': _s(case.account_id or ''),
                    'contact_id': _s(case.contact_id or ''),

                    'lily_created': _s(case.created.strftime("%d %b %Y - %H:%M:%S")),
                    'lily_modified': _s(case.modified.strftime("%d %b %Y - %H:%M:%S")),
                }
                writer.writerow(data)

        filename = 'exports/tenant_{}/cases.csv'.format(tenant_id)
        default_storage.save(name=filename, content=csvfile)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported cases. \n\n')
