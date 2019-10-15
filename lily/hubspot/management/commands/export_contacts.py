import StringIO
import csv

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.contacts.models import Contact
from lily.hubspot.prefetch_objects import phone_prefetch, accounts_prefetch, twitter_prefetch, \
    email_addresses_prefetch, addresses_prefetch
from lily.hubspot.utils import get_phone_numbers, get_mappings
from lily.socialmedia.models import SocialMedia
from lily.tenant.middleware import set_current_user
from lily.tenant.models import Tenant
from lily.users.models import LilyUser
from lily.utils.models.models import EmailAddress


def _s(value):
    return unicode(value).encode('utf-8')


field_names = (
    'contact_id',
    'account_id',

    'first_name',
    'last_name',
    'gender',
    'description',
    'status',

    'phone',
    'mobile_phone',
    'email',

    'twitterhandle',

    'lily_created',
    'lily_modified',
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with contacts export')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())
        tenant = Tenant.objects.get(id=tenant_id)
        m = get_mappings(tenant_id)

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        contact_qs = Contact.objects.filter(
            is_deleted=False
        ).prefetch_related(
            accounts_prefetch,
            twitter_prefetch,
            phone_prefetch,
            addresses_prefetch,
            email_addresses_prefetch
        ).order_by('pk')
        paginator = Paginator(contact_qs, 1000)

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            contact_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for contact in contact_list:
                account_id = contact.prefetched_accounts[0].pk if contact.prefetched_accounts else ''
                twitter = contact.prefetched_twitters[0] if contact.prefetched_twitters else SocialMedia()
                emails = contact.prefetched_email_addresses
                phone_numbers = get_phone_numbers(contact, tenant)

                if emails:
                    primary_email = emails[0]

                    if len(emails) > 1:
                        for email in emails[1:]:
                            data = {
                                'first_name': _s(contact.first_name),
                                'last_name': _s(contact.last_name),
                                'email': _s(email.email_address),
                                'account_id': _s(account_id),
                            }
                            writer.writerow(data)
                else:
                    primary_email = EmailAddress()

                data = {
                    'contact_id': _s(contact.pk),
                    'account_id': _s(account_id),

                    'first_name': _s(contact.first_name),
                    'last_name': _s(contact.last_name),
                    'gender': _s(contact.get_gender_display().upper()),
                    'description': _s(contact.description),
                    'status': _s(m.contact_status_to_contact_status_mapping[contact.status]),

                    'phone': _s(phone_numbers),
                    'email': _s(primary_email.email_address),

                    'twitterhandle': _s(twitter.username or ''),

                    'lily_created': _s(contact.created.strftime("%d %b %Y - %H:%M:%S")),
                    'lily_modified': _s(contact.modified.strftime("%d %b %Y - %H:%M:%S")),
                }
                writer.writerow(data)

        filename = 'exports/tenant_{}/contacts.csv'.format(tenant_id)
        default_storage.save(name=filename, content=csvfile)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported contacts. \n\n')
