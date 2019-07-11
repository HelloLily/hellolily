import freemail
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q

from lily.accounts.models import Website, Account
from lily.contacts.models import Contact, Function
from lily.hubspot.prefetch_objects import accounts_prefetch, email_addresses_prefetch
from lily.hubspot.utils import get_accounts_without_website, get_contacts_without_email_address, _strip_website
from lily.tags.models import Tag
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser
from lily.utils.functions import clean_website
from lily.utils.models.models import EmailAddress


def find_suitable_website_from_email_addresses(email_address_list):
    for email in email_address_list:
        email_address = email.email_address.encode('ascii', errors='ignore')
        if freemail.is_free(email_address):
            continue
        else:
            return email_address.rsplit('@')[-1]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, tenant_id, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>') + '  Starting fixing. \n\n')
        set_current_user(LilyUser.objects.filter(tenant_id=tenant_id, is_active=True).first())

        self.fix_accounts(tenant_id)
        self.fix_contacts(tenant_id)
        self.put_accounts_emails_in_contacts()
        self.delete_accounts_with_cold_email_tag()

        self.stdout.write(self.style.SUCCESS('>>') + '  Successfully fixed. \n\n')

    def fix_accounts(self, tenant_id):
        self.stdout.write(u'Fixing accounts:')

        account_id_list = [a[0] for a in get_accounts_without_website(tenant_id)]
        account_list = Account.objects.filter(
            id__in=account_id_list
        ).prefetch_related(
            email_addresses_prefetch
        )

        paginator = Paginator(account_list, 100)
        self.stdout.write(u'    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            object_list = paginator.page(page_number).object_list

            self.stdout.write('    Page: {} / {}'.format(page_number, paginator.num_pages))
            for account in object_list:
                website = find_suitable_website_from_email_addresses(account.prefetched_email_addresses)

                if not website:
                    # No website was found, so try the contact email addresses.
                    contact_list = Contact.objects.filter(
                        functions__account_id=account.pk
                    ).prefetch_related(
                        email_addresses_prefetch
                    )

                    for contact in contact_list:
                        website = find_suitable_website_from_email_addresses(contact.prefetched_email_addresses)

                        if website:
                            break

                if not website or Website.objects.filter(website=clean_website(website), account=account).exists():
                    website = 'account-{}-from-import.nl'.format(account.pk)

                account.websites.add(Website.objects.create(
                    website=website,
                    account=account,
                    is_primary=True
                ))

    def fix_contacts(self, tenant_id):
        self.stdout.write(u'Fixing contacts:')

        contact_id_list = [c[0] for c in get_contacts_without_email_address(tenant_id)]
        contact_list = Contact.objects.filter(
            id__in=contact_id_list
        ).prefetch_related(
            accounts_prefetch
        )

        paginator = Paginator(contact_list, 100)
        self.stdout.write(u'    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            object_list = paginator.page(page_number).object_list

            self.stdout.write(u'    Page: {} / {}'.format(page_number, paginator.num_pages))
            for contact in object_list:
                account = contact.prefetched_accounts[0] if contact.prefetched_accounts else None
                website = None
                if account:
                    website = account.websites.exclude(website='http://').order_by('-is_primary').first()

                if website:
                    new_email = u'{}@{}'.format(
                        contact.full_name.replace(' ', '.').lower(),
                        _strip_website(website.website)
                    ).replace(' ', '')
                else:
                    new_email = u'contact-{}@data-from-import.nl'.format(contact.pk)

                email_address = EmailAddress.objects.create(
                    email_address=new_email,
                    status=EmailAddress.PRIMARY_STATUS,
                    tenant_id=tenant_id
                )
                contact.email_addresses.add(email_address)

    def put_accounts_emails_in_contacts(self):
        self.stdout.write(u'Fixing accounts with email addresses:')

        # Get all active email addresses for accounts, where the email address is not already included in a contact.
        account_email_addresses = EmailAddress.objects.prefetch_related('account_set').filter(
            account__is_deleted=False,
        ).exclude(
            Q(status=EmailAddress.INACTIVE_STATUS) | Q(email_address__in=EmailAddress.objects.filter(
                contact__is_deleted=False
            ).values_list('email_address', flat=True).distinct())
        )

        paginator = Paginator(account_email_addresses, 100)
        self.stdout.write(u'    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            object_list = paginator.page(page_number).object_list

            self.stdout.write(u'    Page: {} / {}'.format(page_number, paginator.num_pages))
            for email_address in object_list:
                account = email_address.account_set.first()

                with transaction.atomic():
                    # Create the new contact.
                    contact = Contact.objects.create(
                        first_name=email_address.email_address,
                    )

                    # Copy the email address to attach it to the contact.
                    email = EmailAddress.objects.create(
                        email_address=email_address.email_address,
                        status=EmailAddress.PRIMARY_STATUS,
                    )
                    contact.email_addresses.add(email)

                    # Attach the contact to the account.
                    Function.objects.create(
                        account=account,
                        contact=contact
                    )

    def delete_accounts_with_cold_email_tag(self):
        self.stdout.write(u'Deleting accounts with cold email tags:')

        account_content_type = Account().content_type
        account_ids = Tag.objects.filter(
            name='cold email',
            content_type=account_content_type
        ).values_list('object_id', flat=True)
        account_list = Account.objects.filter(id__in=account_ids, is_deleted=False)

        paginator = Paginator(account_list, 100)
        self.stdout.write(u'    Page: 0 / {}    ({} items)'.format(paginator.num_pages, paginator.count))
        for page_number in paginator.page_range:
            object_list = paginator.page(page_number).object_list

            self.stdout.write(u'    Page: {} / {}'.format(page_number, paginator.num_pages))
            for account in object_list:
                account.delete()
