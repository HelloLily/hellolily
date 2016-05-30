import csv
import gc
import logging
import os
from datetime import datetime

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import DataError
from django.utils import timezone

from lily.accounts.models import Account, Website
from lily.contacts.models import Contact, Function
from lily.socialmedia.models import SocialMedia
from lily.users.models import LilyUser
from lily.utils.functions import parse_address, is_int, parse_phone_number
from lily.utils.models.models import Address, PhoneNumber, EmailAddress
from lily.utils.countries import COUNTRIES


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Import accounts and then contacts from separate csv files.

E.g.:
* sugarcsvimport accounts /local/sandbox/hellolily-import/partners.csv  10
* sugarcsvimport contacts /local/sandbox/hellolily-import/contacten.csv  10
"""
    # Some countries are not in 2-code or misspelled
    country_map = {
        'NEDERLAND': 'NL',
        'NETHERLANDS': 'NL',
        'THE NETHERLANDS': 'NL',
        'HOLLAND': 'NL',
        'NDERLAND': 'NL',
        'NEDELAND': 'NL',
        'NLN': 'NL',
        'THE NETHERLAND': 'NL',
        'SURINAME': 'SR',
        'BELGIE': 'BE',
        'BELGIUM': 'BE',
        'BELGI&#235;': 'BE',
        'DUITSLAND': 'DE',
        'GERMANY': 'DE',
        'LUXEMBOURG': 'LU',
        'MAROC': 'MA',
        'UK': 'GB',
        'UNITED KINGDOM': 'GB',
        'FINLAND': 'FI',
        'NEDERLANDSE ANTILLEN': 'AN',
        'CANADA': 'CA',
        'SPAIN': 'ES',
        'SPANJE': 'ES',
        'ESPANA': 'ES',
        'USA': 'US',
        'U.S.A.': 'US',
        'AUSTRALIA': 'AU',
        'IRELAND': 'IR',
        'FRANKRIJK': 'FR',
        'FRANCE': 'FR',
        'POLEN': 'PL',
        'MALTA': 'MT',
        'PHILIPPINES': 'PH',
    }

    account_column_attribute_mapping = {
        'VoIPGRID ID': 'customer_id',
        'Name': 'name',
        '': 'flatname',
        '': 'status',
        '': 'company_size',
        '': 'logo',
        '': 'legalentity',
        '': 'taxnumber',
        '': 'bankaccountnumber',
        'KvK': 'cocnumber',
        '': 'iban',
        '': 'bic',
        'ID': 'import_id',
        'Date Created': 'created',
    }

    account_status_mapping = {
        'Active': 'active',
        'Inactive': 'inactive',
        'Suspended': 'inactive',
        'Unknown': 'unknown',
    }

    contact_column_attribute_mapping = {
        'ID': 'import_id',
        'First Name': 'first_name',
        '': 'preposition',
        'Last Name': 'last_name',
        '': 'gender',
        '': 'title',
        '': 'status',
        '': 'picture',
        'Description': 'description',
        '': 'salutation',
        'Date Created': 'created',
    }

    unmatched_accounts = list()

    duplicate_contacts = list()
    unmatched_contacts = list()

    country_codes = set([country[0] for country in COUNTRIES])
    user_mapping = {}
    already_logged = set()

    def handle(self, model, csvfile, tenant_pk, sugar='1', **kwargs):
        self.tenant_pk = tenant_pk
        self.sugar_import = sugar == '1'

        # Get user mapping from env vars.
        user_string = os.environ.get('USERMAPPING')
        for user in user_string.split(';'):
            sugar, lily = user.split(':')
            self.user_mapping[sugar] = lily

        if model in ['account', 'accounts']:
            logger.info('importing accounts started')

            for row in self.read_csvfile(csvfile):
                self._create_account_data(row)
                gc.collect()

            unmatched_filename = self.write_to_file(self.unmatched_accounts, 'unmatched_accounts')

            logger.info('Unmatched Accounts file %s' % unmatched_filename)

            logger.info('importing accounts finished')

        elif model in ['contact', 'contacts']:
            logger.info('importing contacts started')

            for row in self.read_csvfile(csvfile):
                self._create_contact_data(row)
                gc.collect()

            duplicates_filename = self.write_to_file(self.duplicate_contacts, 'duplicate_contacts')
            unmatched_filename = self.write_to_file(self.unmatched_contacts, 'unmatched_contacts')

            logger.info('Duplicate Contacts file %s' % duplicates_filename)
            logger.info('Unmatched Contacts file %s' % unmatched_filename)
            logger.info('importing contacts finished')

        else:
            raise Exception('unknown model: %s' % model)

    def read_csvfile(self, file_name):
        """
        Read from path assuming it's a file with ',' separated values.
        """
        # Newlines are breaking correct csv parsing. Write correct temporary file to parse.
        csv_file = default_storage.open(file_name, 'rU')
        reader = csv.DictReader(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
        for row in reader:
            yield row

    def write_to_file(self, item_list, name):
        i = 0
        file_name = None
        while True:
            file_name = '%s_%s' % (name, i)
            if not default_storage.exists(file_name):
                break
            else:
                i += 1
        file = default_storage.open(file_name, 'a+')
        for item in item_list:
            file.write(item + "\n")
        file.clos
        return file_name

    def _create_account_data(self, values):
        """
        Create Account from given dict.

        Arguments:
            values (dict): information with account information
        """

        # Create account.
        account_kwargs = dict()
        for column, value in values.items():
            if value and column in self.account_column_attribute_mapping:
                attribute = self.account_column_attribute_mapping.get(column)
                # Set created date to original created date in sugar.
                if attribute == 'created':
                    value = timezone.make_aware(
                        datetime.strptime(str(value), "%d-%m-%Y %H.%M"),
                        timezone.get_current_timezone()
                    )
                account_kwargs[attribute] = value

        if not len(account_kwargs):
            return
        if 'name' not in account_kwargs or not account_kwargs['name']:
            return
        try:
            account = Account.objects.get(
                tenant_id=self.tenant_pk,
                import_id=account_kwargs['import_id']
            )
        except Account.DoesNotExist:
            account = Account.objects.filter(tenant_id=self.tenant_pk, name=account_kwargs['name']).first()
            if not account:
                account = Account(tenant_id=self.tenant_pk)

        for k, v in account_kwargs.items():
            setattr(account, k, v)

        # Extend description with netwerk opstelling information.
        extended_description = ""
        if values.get('Netwerk opstelling'):
            extended_description = ' # Netwerk opstelling: ' + values.get('Netwerk opstelling')
        if not account.description:
            account.description = values.get('Description') + extended_description

        # Status of account.
        status = values.get('Status')

        # Map sugar status to lily status.
        if status and status in self.account_status_mapping:
            status = self.account_status_mapping[status]
        else:
            status = 'unknown'

        account.status = status

        # Satisfy m2m contraints.
        try:
            account.save()
        except DataError:
            self.unmatched_accounts.append(values.get('ID'))
            logger.error(u'DataError for %s' % account_kwargs)
            return

        # Create addresses.
        self._create_address(
            account,
            'visiting',
            values.get('Billing Street'),
            values.get('Billing Postal Code'),
            values.get('Billing City'),
            values.get('Billing Country')
        )
        self._create_address(
            account,
            'shipping',
            values.get('Shipping Street'),
            values.get('Shipping Postal Code'),
            values.get('Shipping City'),
            values.get('Shipping Country')
        )

        # Create email addresses.
        self._create_email_addresses(account, values)

        # Create phone numbers.
        self._create_phone(account, 'work', values.get('Office Phone'))
        self._create_phone(account, 'work', values.get('Alternate Phone'))
        # In the create phone this will be converted to normal type Fax instead of other.
        self._create_phone(account, 'other', values.get('Fax'), other_type='fax')

        # Create website.
        self._create_website(account, values.get('Website'))

        # Create social media.
        self._create_social_media(account, 'linkedin', values.get('LinkedIn'))
        self._create_social_media(account, 'twitter', values.get('Twitter'))

        # Map sugar user to lily user and set assigned to.
        user_id = values.get('Assigned To')
        if user_id and user_id in self.user_mapping:
            try:
                account.assigned_to = LilyUser.objects.get(
                    pk=self.user_mapping[user_id],
                    tenant_id=self.tenant_pk
                )
            except LilyUser.DoesNotExist:
                if user_id not in self.already_logged:
                    self.already_logged.add(user_id)
                    logger.warning(u'Assignee does not exists as an LilyUser. %s' % user_id)
        else:
            # Only log when user_name not empty.
            if user_id and user_id not in self.already_logged:
                self.already_logged.add(user_id)
                logger.warning(u'Assignee does not have an usermapping. %s' % user_id)

        account.save()

    def _create_contact_data(self, values):
        """
        Create Contact instance for given dict.

        Arguments:
            values (dict):

        """
        # Map columns and values to Contact model attributes
        contact_kwargs = dict()
        for column, value in values.items():
            if value and column in self.contact_column_attribute_mapping:
                attribute = self.contact_column_attribute_mapping.get(column)
                # Set created date to original created date in sugar.
                if attribute == 'created':
                    value = timezone.make_aware(
                        datetime.strptime(str(value), "%d-%m-%Y %H.%M"),
                        timezone.get_current_timezone()
                    )
                contact_kwargs[attribute] = value

        # Check if we can find a first and or last name
        first, last = False, False
        if 'first_name' in contact_kwargs and contact_kwargs['first_name']:
            first = True
            contact_kwargs['first_name'] = contact_kwargs['first_name'][:254]
        if 'last_name' in contact_kwargs and contact_kwargs['last_name']:
            last = True
            contact_kwargs['last_name'] = contact_kwargs['last_name'][:254]

        if not (first or last):
            self.unmatched_contacts.append(values.get('ID'))
            logger.warning(u'No first or last name for contact. %s' % contact_kwargs)
            return

        gender = Contact.UNKNOWN_GENDER
        if values.get('Salutation') in ['Mr.', 'Dhr.', 'mr.']:
            gender = Contact.MALE_GENDER
        elif values.get('Salutation') in ['Ms.', 'Mrs.']:
            gender = Contact.FEMALE_GENDER
        contact_kwargs['gender'] = gender

        contact_kwargs['tenant_id'] = self.tenant_pk
        contact_kwargs['salutation'] = Contact.INFORMAL
        try:
            contact = Contact.objects.get(tenant_id=self.tenant_pk, import_id=contact_kwargs['import_id'])
        except Contact.DoesNotExist:
            # Only check on name, if both first and last name exist:
            # Those were added before the import_id field was introduced.
            if first and last:
                try:
                    contact = Contact.objects.get(
                        tenant_id=self.tenant_pk,
                        first_name=contact_kwargs['first_name'],
                        last_name=contact_kwargs['last_name']
                    )
                except Contact.DoesNotExist:
                    contact = Contact(tenant_id=self.tenant_pk)
                except Contact.MultipleObjectsReturned:

                    if values.get('Email Address'):
                        # Check for contact with matching email
                        email_address_kwargs = dict()
                        email_address_kwargs['email_address'] = values.get('Email Address')
                        email_address_kwargs['tenant_id'] = self.tenant_pk

                        contact_list = Contact.objects.filter(
                            tenant_id=self.tenant_pk,
                            first_name=contact_kwargs['first_name'],
                            last_name=contact_kwargs['last_name'],
                            email_addresses__email_address=values.get('Email Address'),
                            email_addresses__tenant_id=self.tenant_pk)

                        if not contact_list.exists():
                            contact = Contact(tenant_id=self.tenant_pk)
                        else:
                            # Pick first we do not delete the others
                            # incase they are duplicate but contain a
                            # lot more info or are connected to a other
                            # account
                            contact = contact_list.first()
                            if len(contact_list) > 1:
                                self.duplicate_contacts.append(
                                    contact_kwargs['first_name'] + " " + contact_kwargs['last_name']
                                )
                    else:
                        self.unmatched_contacts.append(values.get('ID'))
                        return
            else:
                # What to do if a contact has no first and last name
                self.unmatched_contacts.append(values.get('ID'))
                return

        for k, v in contact_kwargs.items():
            setattr(contact, k, v)

        contact.save()

        # Create addresses
        self._create_address(
            contact,
            'billing',
            values.get('Primary Address Street'),
            values.get('Primary Address Postal Code'),
            values.get('Primary Address City'),
            values.get('Primary Address Country')
        )
        self._create_address(
            contact,
            'shipping',
            values.get('Alternate Address Street'),
            values.get('Alternate Address Postal Code'),
            values.get('Alternate Address City'),
            values.get('Alternate Address Country')
        )

        # Create email addresses
        self._create_email_addresses(contact, values)

        # Create phone numbers
        self._create_phone(contact, 'work', values.get('Office Phone'))
        self._create_phone(contact, 'work', values.get('Other Phone'))
        self._create_phone(contact, 'mobile', values.get('Mobile Phone'))
        self._create_phone(contact, 'other', values.get('Fax'), other_type='fax')
        self._create_phone(contact, 'other', values.get('Home Phone'), other_type='home')

        # Create social media
        self._create_social_media(contact, 'twitter', values.get('Twitter'))

        try:
            account = Account.objects.get(name=values.get('Account Name'), tenant_id=self.tenant_pk)
        except Account.DoesNotExist:
            account = None
        except Account.MultipleObjectsReturned:
            account = Account.objects.filter(name=values.get('Account Name'), tenant_id=self.tenant_pk).first()
            logger.warning('Pick first account of multiple accounts for name: %s' % values.get('Account Name'))

        if account:
            # Create function (link with account)
            function, created = Function.objects.get_or_create(account=account, contact=contact)
            title = (values.get('Title') + " " + values.get("Department"))[:50]
            function.title = title
            function.save()

        contact.save()

    def _create_address(self, instance, type, address, postal_code, city, country, primary=False):
        """
        Create an Address for given instance

        Arguments:
            instance (instance): instance to add Address to.
            type (str): kind of address
            address (str): street and number
            postal_code (str): postal code
            city (str): city
            country (str): country
        """
        if address and city:
            street, number, complement = parse_address(address)
            address_kwargs = dict()
            address_kwargs['type'] = type
            address_kwargs['street'] = street

            # Set streetnumber.
            if is_int(number) and int(number) < 32766:
                address_kwargs['street_number'] = int(number)
            address_kwargs['complement'] = complement

            # Set postal code.
            if len(postal_code) > 10:
                postal_code = postal_code[:10]
            address_kwargs['postal_code'] = postal_code
            address_kwargs['city'] = city

            # Check if country is present.
            if country:
                country = country.upper().strip()
                country = self.country_map.get(country, country)

                # In case of unkown county leave empty.
                if country and len(country) > 2 or country not in self.country_codes:
                    country = ''

                # Set country.
                address_kwargs['country'] = country

            # Set tenant.
            address_kwargs['tenant_id'] = self.tenant_pk

            # Check if adress does not already exists to avoid duplicates.
            if not instance.addresses.filter(
                    street=address_kwargs['street'],
                    city=address_kwargs['city']
            ).exists():
                try:
                    address = Address.objects.create(**address_kwargs)
                except DataError:
                    logger.warning('could not create address: %s' % address_kwargs)
                else:
                    instance.addresses.add(address)
            else:
                address_kwargs.pop('tenant_id')
                instance.addresses.filter(
                    street=address_kwargs['street'],
                    city=address_kwargs['city']
                ).update(**address_kwargs)

    def _create_email_addresses(self, instance, values):
        """
        Creates EmailAddresses for given instance

        Arguments:
            instance (instance): instance to add EmailAddresses to
            values (dict): dict of email address info
        """
        emails = list()
        emails.append((values.get('Email Address'), True))
        non_primary_emails = values.get('Non Primary E-mails')
        if non_primary_emails:
            for email in non_primary_emails.split(';'):
                emails.append((email, False))

        for email, is_primary in emails:
            self._create_email_address(instance, email, is_primary)

    def _create_email_address(self, instance, email, is_primary=True):
        """
        Creates EmailAddress for given instance

        Arguments:
            instance (instance): instance to add EmailAddress to
            email (str): string with email address
            is_primary (boolean): True if emailaddress is the primary
                email address for instance
        """
        if email and len(email) > 2:
            email_address_kwargs = dict()
            email_address_kwargs['email_address'] = email
            email_address_kwargs['status'] = EmailAddress.PRIMARY_STATUS if is_primary else EmailAddress.OTHER_STATUS
            email_address_kwargs['tenant_id'] = self.tenant_pk
            if not instance.email_addresses.filter(**email_address_kwargs).exists():
                email_address = EmailAddress.objects.create(**email_address_kwargs)
                instance.email_addresses.add(email_address)

    def _create_phone(self, instance, type, number, other_type=None):
        """
        Creates PhoneNumber for given instance

        Arguments:
            instance (instance): instance to add PhoneNumber to
            type (str): kind of phone number
            number (str): unformatted phone number
            other_type (str) optional: given if not default phone number type
        """
        if number and len(number) > 2:
            phone_kwargs = dict()
            phone_kwargs['type'] = type
            phone_kwargs['other_type'] = other_type
            phone_kwargs['number'] = parse_phone_number(number)
            phone_kwargs['tenant_id'] = self.tenant_pk

            phone_number_list = instance.phone_numbers.filter(**phone_kwargs)

            if not phone_number_list.exists():
                # Other types are ugly for phonenumbers.
                if other_type is not None:
                    phone_kwargs['type'] = phone_kwargs['other_type']
                    phone_kwargs['other_type'] = None

                # Recheck if it exists without the othertype.
                if not instance.phone_numbers.filter(**phone_kwargs).exists():
                    phone_number = PhoneNumber.objects.create(**phone_kwargs)
                    instance.phone_numbers.add(phone_number)
            else:

                # Keep first in list and delete all the others.
                for i, phone_number in enumerate(phone_number_list):
                    if i == 0:
                        # When othertype given set normal type instead for save.
                        if other_type is not None:
                            phone_number.type = phone_number.other_type
                            phone_kwargs['type'] = phone_number.other_type
                            phone_number.other_type = None
                            phone_kwargs['other_type'] = None
                            if not instance.phone_numbers.filter(**phone_kwargs).exists():
                                phone_number.save()
                    else:
                        phone_number.delete()

    def _create_social_media(self, instance, name, username):
        """
        Create a SocialMedia instance for given instance

        Arguments:
            instance (instance): instance to add SocialMedia to
            name (str): name of social media network
            username (str): profile name on the network
        """
        if username and len(username) < 100:
            if username.startswith('/'):
                username = username[1:]
            if not username:
                return
            if not instance.social_media.filter(name=name, username=username).exists():
                sm = SocialMedia.objects.create(tenant_id=self.tenant_pk,
                                                name=name,
                                                username=username)
                instance.social_media.add(sm)

    def _create_website(self, account, url):
        """
        Add Website instance to given account

        Arguments:
            account (instance): Account to add Website to.
            url (str): url of website
        """
        if url and len(url) > 2 and url != 'http://':
            website_kwargs = dict()
            website_kwargs['tenant_id'] = self.tenant_pk
            website_kwargs['website'] = url
            website_kwargs['account'] = account
            website_kwargs['is_primary'] = True
            Website.objects.get_or_create(**website_kwargs)
