import csv
import time

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from lily.accounts.models import Account, Website
from lily.cases.models import Case
from lily.contacts.models import Contact, Function
from lily.deals.models import Deal
from lily.socialmedia.models import SocialMedia
from lily.tags.models import Tag
from lily.tenant.models import Tenant
from lily.utils.models.models import Address, EmailAddress, PhoneNumber
from lily.utils.countries import COUNTRIES


class Command(BaseCommand):
    help = """Load Nimble CSV accounts and contacts files, optionally truncating the tenant."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            dest='tenant',
            action='store',
            default='',
            help='Specify a tenant to create the testdata in, or leave blank to create new.'
        )
        parser.add_argument(
            '--dialcode',
            dest='dialcode',
            action='store',
            help='Specify default international dialcode for local formatted phone numbers.'
        )
        parser.add_argument(
            '--country',
            dest='country',
            action='store',
            help='Specify default country for addresses. (2-letter iso code)'
        )
        parser.add_argument(
            '--truncate',
            dest='truncate',
            action='store_true',
            help='If the tenant should be truncated. Only makes sense when using existing tenant.'
        )
        parser.add_argument(
            '--verbose',
            dest='verbose',
            action='store_true',
            help='If extra output should be printed.'
        )

    def clean_phone(self, phone):
        """Cleans a phone number by removing chars and prefixing with dialcode."""
        if self.verbose:
            print 'before %s' % phone
        # Strip all nonsense characters
        for char in [' ', '-', '(', ')']:
            phone = ''.join(phone.split(char))
        if len(phone) >= 11:
            # This is international notation, prefix with '+' if not already present.
            if not phone.startswith('+'):
                phone = '+%s' % phone
        else:
            # Not an international notation.
            if phone.startswith('0'):
                phone = phone[1:]
            phone = '+%s%s' % (self.dialcode, phone)
        if self.verbose:
            print 'after  %s' % phone
        return phone

    def handle(self, *args, **options):
        """Main method for iterating over all accounts and contacts in the csv."""
        self.verbose = options.get('verbose')
        self.dialcode = options['dialcode']
        assert self.dialcode, 'Need option dialcode.'
        self.country = options['country']
        assert self.country, 'Need option country.'
        self.country = self.country.upper()

        tenantOption = options.get('tenant')
        if not tenantOption:
            tenant = Tenant()
            tenant.save()
            print 'Created new tenant %s' % tenant.id
        else:
            tenant = Tenant.objects.get(pk=int(tenantOption.strip()))
            print 'Using existing tenant %s' % tenant.id

        if options['truncate']:
            print "Warning, truncating tenant %s in a few seconds.." % tenant
            time.sleep(5)
            for model in [Deal, Case, Website, PhoneNumber, SocialMedia, Tag, EmailAddress, Address,
                          Account, Contact]:
                model.objects.filter(tenant=tenant).delete()

        accounts = {}
        contacts = {}
        with open('accounts.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            csvfile.readline()  # skip header
            for row in reader:
                name = row[0]
                mobile_phone = row[1]
                work_phone = row[2]
                fax_phone = row[3]
                primary_email = row[4]
                skype = row[5]
                twitter = row[6]
                street = row[7]
                city = row[8]
                state = row[9]
                zipcode = row[10]
                country = row[11]
                work_url = row[12] or row[13]
                description = row[14] or row[15]
                tags = row[19:]

                if name in accounts:
                    print 'Duplicate account: %s ' % name
                    continue

                account = {
                    'name': name,
                    'description': description,
                }
                account_instance = Account.objects.get_or_create(tenant=tenant, **account)[0]

                if skype:
                    social_media = SocialMedia.objects.get_or_create(
                        tenant=tenant, name='other', other_name='skype', username=skype)[0]
                    account_instance.social_media.add(social_media)

                if twitter:
                    social_media = SocialMedia.objects.get_or_create(
                        tenant=tenant, name='twitter', username=twitter,
                        profile_url='https://twitter.com/%s' % twitter)[0]
                    account_instance.social_media.add(social_media)

                for tag in tags:
                    if tag:
                        content_type = ContentType.objects.get_for_model(Account)
                        object_id = account_instance.id
                        Tag.objects.get_or_create(
                            tenant=tenant, content_type=content_type, object_id=object_id, name=tag)

                if work_url:
                    if not (work_url.startswith('http://') or work_url.startswith('https://')):
                        work_url = 'http://%s' % work_url
                    website = Website(tenant=tenant, website=work_url)
                    account_instance.websites.add(website)

                if street:
                    country_code = self.country
                    for code, country_name in COUNTRIES:
                        if country == country_name:
                            if self.verbose:
                                print 'found country %s' % country
                            country_code = code
                    address_instance = Address.objects.get_or_create(
                        tenant=tenant, street=street, postal_code=zipcode, state_province=state,
                        city=city, country=country_code)[0]
                    account_instance.addresses.add(address_instance)

                for number, number_type in [(mobile_phone, 'mobile'), (work_phone, 'work'), (fax_phone, 'fax')]:
                    if number:
                        number = self.clean_phone(number)
                        phone = PhoneNumber.objects.get_or_create(
                            tenant=tenant, type=number_type, number=number)[0]
                        account_instance.phone_numbers.add(phone)

                if primary_email:
                    email = EmailAddress.objects.get_or_create(
                        tenant=tenant, email_address=primary_email, status=EmailAddress.PRIMARY_STATUS)[0]
                    account_instance.email_addresses.add(email)

                account_instance.save()
                account['instance'] = account_instance
                accounts[name] = account

        with open('contacts.csv', 'rb') as csvfile:
            csvfile.readline()  # skip header
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                first_name = row[0]
                last_name = row[1]
                account_name = row[2]
                title = row[3]
                work_phone = row[4]
                work2_phone = row[5]
                home_phone = row[6]
                mobile_phone = row[7]
                work3_phone = row[8]
                work4_phone = row[9]
                fax_phone = row[10]
                other_phone = row[11]
                emails = row[12:16]
                skype = row[16]
                twitters = row[17:20]
                facebook = row[20]
                linkedin = row[21]
                gplus = row[22]
                addresses = [row[23:28], row[28:33], row[33:38], row[38:43]]  # 4 addresses
                websites = row[43:55]
                # Join some descriptions into a single string.
                # (Including tags, because they are quite messy in the csv, for example some have spaces.)
                description = ', '.join([title] + [desc for desc in row[55:] if desc])

                if '@' in first_name:
                    print 'Email address for name %s ' % first_name
                    continue

                if not account_name:
                    print 'Empty account name for %s, %s' % (first_name, last_name)
                    account_name = None
                    account_instance = None
                else:
                    account_instance = accounts[account_name]['instance']

                contact_key = '%s, %s, %s' % (first_name, last_name, account_name)

                if contact_key in contacts:
                    print 'Duplicate contact: %s ' % contact_key
                    continue

                contact = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'description': description,
                }

                contact_instance = Contact.objects.get_or_create(tenant=tenant, **contact)[0]

                for website in websites:
                    if website:
                        if not (website.startswith('http://') or website.startswith('https://')):
                            website = 'http://%s' % website
                        social_media = SocialMedia.objects.get_or_create(
                            tenant=tenant, name='other', username=website,
                            profile_url=website)[0]
                        contact_instance.social_media.add(social_media)

                for address in addresses:
                    street, city, state, zipcode, country = address
                    if street or city or state or zipcode or country:
                        country_code = self.country
                        for code, country_name in COUNTRIES:
                            if country == country_name:
                                if self.verbose:
                                    print 'found country %s' % country
                                country_code = code
                        address_instance = Address.objects.get_or_create(
                            tenant=tenant, street=street, postal_code=zipcode, state_province=state,
                            city=city, country=country_code)[0]
                        contact_instance.addresses.add(address_instance)

                if skype:
                    social_media = SocialMedia.objects.get_or_create(
                        tenant=tenant, name='other', other_name='skype', username=skype)[0]
                    contact_instance.social_media.add(social_media)

                if linkedin:
                    social_media = SocialMedia.objects.get_or_create(
                        tenant=tenant, name='linkedin', username=linkedin,
                        profile_url=linkedin)[0]
                    contact_instance.social_media.add(social_media)

                if gplus:
                    social_media = SocialMedia.objects.get_or_create(
                        tenant=tenant, name='googleplus', username=gplus,
                        profile_url=gplus)[0]
                    contact_instance.social_media.add(social_media)

                if facebook:
                    start_username = facebook.rfind('/') + 1
                    facebook = facebook[start_username:]
                    social_media = SocialMedia.objects.get_or_create(
                        tenant=tenant, name='facebook', username=facebook,
                        profile_url='https://facebook.com/%s' % facebook)[0]
                    contact_instance.social_media.add(social_media)

                for twitter in twitters:
                    if twitter:
                        social_media = SocialMedia.objects.get_or_create(
                            tenant=tenant, name='twitter', username=twitter,
                            profile_url='https://twitter.com/%s' % twitter)[0]
                        contact_instance.social_media.add(social_media)

                first_added = False
                for email_address in emails:
                    if email_address:
                        if first_added:
                            email_status = EmailAddress.OTHER_STATUS
                        else:
                            email_status = EmailAddress.PRIMARY_STATUS
                        email = EmailAddress.objects.get_or_create(
                            tenant=tenant, email_address=email_address, status=email_status)[0]
                        contact_instance.email_addresses.add(email)
                        first_added = True

                for number, number_type in [
                    (mobile_phone, 'mobile'), (work_phone, 'work'), (fax_phone, 'fax'), (work2_phone, 'work'),
                    (work3_phone, 'work'), (work4_phone, 'work'), (other_phone, 'other'), (home_phone, 'home')
                ]:
                    if number:
                        number = self.clean_phone(number)
                        phone = PhoneNumber.objects.get_or_create(
                            tenant=tenant, type=number_type, number=number)[0]
                        contact_instance.phone_numbers.add(phone)

                if account_instance:
                    Function.objects.get_or_create(contact=contact_instance, account=account_instance)

                contact_instance.save()
                contacts[contact_key] = contact

        print 'accounts:%s contacts:%s' % (len(accounts), len(contacts)),
