import StringIO
import csv

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from lily.accounts.models import Account, Website
from lily.hubspot.mappings import lilyuser_to_owner_mapping, account_status_to_company_type_mapping
from lily.hubspot.prefetch_objects import (
    website_prefetch, addresses_prefetch, phone_prefetch, social_media_prefetch, tags_prefetch
)
from lily.hubspot.utils import _s, _strip_website
from lily.socialmedia.models import SocialMedia
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser
from lily.utils.models.models import Address, PhoneNumber


field_names = (
    'account_id',
    'name',
    'description',
    'domain',
    'owner',  # assigned_to
    'numberofemployees',  # company_size
    'type',  # status

    'phone',

    'street',
    'city',
    'state',
    'zip',
    'country',

    # legalentity?
    # taxnumber?
    # bankaccountnumber?
    # cocnumber?
    # iban?
    # bic?

    'twitterhandle',
    'linkedin_company_page',
    'facebook_company_page',

    'sells_hardware',
    'freedom_url',

    'lily_created',
    'lily_modified',
)


class Command(BaseCommand):
    help = 'Export accounts for specified tenant id.'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting with accounts export')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        account_qs = Account.objects.filter(
            is_deleted=False
        ).prefetch_related(
            website_prefetch,
            addresses_prefetch,
            phone_prefetch,
            social_media_prefetch,
            tags_prefetch
        ).order_by('pk')
        paginator = Paginator(account_qs, 100)

        self.stdout.write('    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            account_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for account in account_list:
                website = account.prefetched_websites[0] if account.prefetched_websites else Website()
                address = account.prefetched_addresses[0] if account.prefetched_addresses else Address()
                phone = account.prefetched_phone_numbers[0] if account.prefetched_phone_numbers else PhoneNumber()
                social_media = {social.name: social for social in account.prefetched_social_media}
                tags = [tag.name.lower() for tag in account.prefetched_tags]

                f_url = 'https://freedom.voys.nl/client/{}'.format(account.customer_id) if account.customer_id else ''
                data = {
                    'account_id': _s(account.pk),
                    'name': _s(account.name),
                    'description': _s(account.description),
                    'domain': _s(_strip_website(website.website)),
                    'owner': _s(lilyuser_to_owner_mapping.get(account.assigned_to_id, '')),
                    'numberofemployees': _s(account.company_size),
                    'type': _s(account_status_to_company_type_mapping[account.status_id]),
                    'phone': _s(phone.number),
                    'street': _s(address.address),
                    'city': _s(address.city),
                    'state': _s(address.state_province),
                    'zip': _s(address.postal_code),
                    'country': _s(address.country),
                    'twitterhandle': _s(social_media.get('twitter', SocialMedia()).username or ''),
                    'linkedin_company_page': _s(social_media.get('linkedin', SocialMedia()).profile_url or ''),
                    'facebook_company_page': _s(social_media.get('facebook', SocialMedia()).profile_url or ''),

                    'sells_hardware': 'hardware' in tags,
                    'freedom_url': _s(f_url),

                    'lily_created': _s(account.created.strftime("%d %b %Y - %H:%M:%S")),
                    'lily_modified': _s(account.modified.strftime("%d %b %Y - %H:%M:%S")),
                }
                writer.writerow(data)

        filename = 'exports/tenant_{}/companies.csv'.format(tenant_id)
        default_storage.save(name=filename, content=csvfile)

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully exported accounts. \n\n')
