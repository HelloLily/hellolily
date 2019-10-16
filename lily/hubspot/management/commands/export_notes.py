import StringIO
import csv

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.hubspot.utils import _s
from lily.notes.models import Note
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser


field_names = (
    'content',
    'author',
    'pinned',
    'date',
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with notes export. \n\n')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())

        self.export_account_notes(tenant_id)
        self.export_contact_notes(tenant_id)
        self.export_case_notes(tenant_id)
        self.export_deal_notes(tenant_id)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported notes. \n\n')

    def export_account_notes(self, tenant_id):
        content_type = Account().content_type
        filename = 'exports/tenant_{}/notes_for_companies.csv'.format(tenant_id)
        account_id_list = Account.objects.filter(is_deleted=False).values_list('id', flat=True)

        self.export(filename, content_type, account_id_list)

    def export_contact_notes(self, tenant_id):
        content_type = Contact().content_type
        filename = 'exports/tenant_{}/notes_for_contacts.csv'.format(tenant_id)
        contact_id_list = Contact.objects.filter(is_deleted=False).values_list('id', flat=True)

        self.export(filename, content_type, contact_id_list)

    def export_case_notes(self, tenant_id):
        content_type = Case().content_type
        filename = 'exports/tenant_{}/notes_for_tickets.csv'.format(tenant_id)
        case_id_list = Case.objects.filter(is_deleted=False, is_archived=True).values_list('id', flat=True)

        self.export(filename, content_type, case_id_list)

    def export_deal_notes(self, tenant_id):
        content_type = Deal().content_type
        filename = 'exports/tenant_{}/notes_for_deals.csv'.format(tenant_id)
        deal_id_list = Deal.objects.filter(is_deleted=False, is_archived=True).values_list('id', flat=True)

        self.export(filename, content_type, deal_id_list)

    def export(self, filename, content_type, gfk_object_id_list):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with notes export for {}s'.format(content_type.model))

        relation_field_name = '{}_id'.format(content_type.model)

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=field_names + (relation_field_name, ))
        writer.writeheader()

        queryset = Note.objects.filter(
            gfk_content_type=content_type, gfk_object_id__in=gfk_object_id_list, is_deleted=False
        )
        paginator = Paginator(queryset, 1000)

        authors = {user.id: user.full_name for user in LilyUser.objects.all()}

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            note_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for note in note_list:
                content = _s(authors.get(note.author_id) + ' created a note on ' + note.created.strftime("%d %b %Y - %H:%M") + ':\n\n' + note.content)  # noqa
                note_data = {
                    'content': content,
                    'author': _s(note.author_id),
                    'pinned': _s(note.is_pinned),
                    'date': _s(note.created.strftime("%d/%m/%Y")),
                    relation_field_name: _s(note.gfk_object_id),
                }
                writer.writerow(note_data)

        default_storage.save(name=filename, content=csvfile)
        self.stdout.write(self.style.SUCCESS('>>') + '  Done exported notes for {}s. \n\n'.format(content_type.model))
