import logging

from celery.task import task
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from tablib import Dataset

from lily.accounts.models import Account, AccountStatus, Website
from lily.contacts.models import Contact, Function
from lily.importer.models import ImportUpload
from lily.socialmedia.models import SocialMedia
from lily.utils.functions import parse_phone_number
from lily.utils.models.models import EmailAddress, PhoneNumber, Address


logger = logging.getLogger(__name__)


@task(name='import_csv_file', logger=logger, bind=True)
def import_csv_file(self, upload_id, iteration, import_type):
    csv_upload = ImportUpload.objects.get(id=upload_id)
    csv_file = csv_upload.csv
    data = Dataset().load(csv_file.read())
    headers = data.headers

    batch_size = settings.IMPORT_BATCH_SIZE
    start = iteration * batch_size
    end = min(((iteration + 1) * batch_size) - 1, len(data) - 1)

    for i in range(start, end + 1):
        row = dict(zip(headers, data[i]))  # Use headers as keys and data as values.
        if import_type == 'contacts':
            import_contact(row, csv_upload.tenant_id, data.headers)
        else:  # 'accounts'
            import_account(row, csv_upload.tenant_id, data.headers)

    if ((iteration + 1) * batch_size) < len(data):
        import_csv_file.apply_async(
            queue='other_tasks',
            kwargs={
                'upload_id': csv_upload.id,
                'iteration': iteration + 1,
                'import_type': import_type,
            },
            countdown=settings.IMPORT_COUNTDOWN
        )


def import_contact(row, tenant_id, headers):
    # The following set of fields should be present as headers in the uploaded file.
    required_fields = {u'first name', u'last name'}
    # The following set of fields are optional.
    optional_fields = {u'company name', u'email address', u'phone number', u'address', u'postal code', u'city',
                       u'twitter', u'linkedin', u'mobile'}

    # The following headers are present in the uploaded file.
    available_in_upload = set(headers)

    optional_in_upload = optional_fields & available_in_upload
    extra_in_upload = available_in_upload - (required_fields | optional_fields)

    first_name = row.get(u'first name')
    last_name = row.get(u'last name')
    full_name = u'{0} {1}'.format(first_name, last_name)

    contact = new_or_existing_contact(row, tenant_id, optional_in_upload)

    account = None
    email_address = None
    phone_number = None
    address = None
    twitter = None
    linkedin = None
    mobile = None
    try:
        # Use atomic to rollback all intermediate database actions if an error occurs in just one of them.
        with transaction.atomic():
            # All the extra fields excluding 'company' that are present in the upload are placed in the description
            # field.
            description = u''
            extra_in_upload_wo_company = set(extra_in_upload)
            extra_in_upload_wo_company.discard(u'company name')
            for field in extra_in_upload_wo_company:
                if row.get(field):
                    description += '{0}: {1}\n'.format(field.capitalize(), row.get(field))

            contact.description = description
            contact.save()

            if u'company name' in optional_in_upload and row.get(u'company name'):
                company_name = row.get(u'company name')
                # Not using get_or_create() to make use of the skip_signal construction.
                try:
                    account = Account.objects.get(name=company_name, tenant_id=tenant_id, is_deleted=False)
                except Account.DoesNotExist:
                    account_status = AccountStatus.objects.get(name='Relation', tenant_id=tenant_id)
                    account = Account(
                        name=company_name,
                        tenant_id=tenant_id,
                        status=account_status
                    )
                    account.skip_signal = True
                    account.save()

            if u'email address' in optional_in_upload and row.get(u'email address'):
                formatted_email_address = row.get(u'email address').lower()
                if not contact.email_addresses.filter(email_address=formatted_email_address).exists():
                    email_address = EmailAddress(
                        email_address=formatted_email_address,
                        status=EmailAddress.PRIMARY_STATUS,
                        tenant_id=tenant_id
                    )
                    email_address.skip_signal = True
                    email_address.save()

            if u'phone number' in optional_in_upload and row.get(u'phone number'):
                formatted_phone_number = parse_phone_number(row.get(u'phone number'))
                if not contact.phone_numbers.filter(number=formatted_phone_number).exists():
                    phone_number = PhoneNumber(
                        number=formatted_phone_number,
                        tenant_id=tenant_id
                    )
                    phone_number.skip_signal = True
                    phone_number.save()

            # An Address consists of multiple, optional fields. So create or update the instance.
            if u'address' in optional_in_upload and row.get(u'address'):
                address = Address(
                    address=row.get(u'address'),
                    type='visiting',
                    tenant_id=tenant_id
                )
                address.skip_signal = True
                address.save()

            if u'postal code' in optional_in_upload and row.get(u'postal code'):
                if address:
                    address.postal_code = row.get(u'postal code')
                else:
                    address = Address(
                        postal_code=row.get(u'postal code'),
                        type='visiting',
                        tenant_id=tenant_id
                    )
                address.skip_signal = True
                address.save()

            if u'city' in optional_in_upload and row.get(u'city'):
                if address:
                    address.city = row.get(u'city')
                else:
                    address = Address(
                        city=row.get(u'city'),
                        type='visiting',
                        tenant_id=tenant_id
                    )
                address.skip_signal = True
                address.save()

            if u'twitter' in optional_in_upload and row.get(u'twitter'):
                twitter = SocialMedia(
                    name='twitter',
                    username=row.get(u'twitter'),
                    profile_url='https://twitter.com/{0}'.format(row.get(u'twitter')),
                    tenant_id=tenant_id
                )
                twitter.skip_signal = True
                twitter.save()

            if u'linkedin' in optional_in_upload and row.get(u'linkedin'):
                linkedin = SocialMedia(
                    name='linkedin',
                    username=row.get(u'linkedin'),
                    profile_url='https://www.linkedin.com/in/{0}'.format(row.get(u'linkedin')),
                    tenant_id=tenant_id
                )
                linkedin.skip_signal = True
                linkedin.save()

            if u'mobile' in optional_in_upload and row.get(u'mobile'):
                formatted_phone_number = parse_phone_number(row.get(u'mobile'))
                if not contact.phone_numbers.filter(number=formatted_phone_number).exists():
                    mobile = PhoneNumber(
                        number=formatted_phone_number,
                        tenant_id=tenant_id,
                        type='mobile'
                    )
                    mobile.skip_signal = True
                    mobile.save()

    except Exception as e:
        # On an exception all database actions are rolled back. Because of the skip_signal=True no row is added to the
        # search index.
        logger.error(u'Import error for {}: {}'.format(full_name, e))
    else:
        if email_address:
            email_address.skip_signal = False
            email_address.save()
            contact.email_addresses.add(email_address)
        if phone_number:
            phone_number.skip_signal = False
            phone_number.save()
            contact.phone_numbers.add(phone_number)
        if address:
            address.skip_signal = False
            address.save()
            contact.addresses.add(address)
        if twitter:
            twitter.skip_signal = False
            twitter.save()
            contact.social_media.add(twitter)
        if linkedin:
            linkedin.skip_signal = False
            linkedin.save()
            contact.social_media.add(linkedin)
        if account:
            account.skip_signal = False
            account.save()

            if not Function.objects.filter(account=account, contact=contact).exists():
                Function.objects.create(account=account, contact=contact)
        if mobile:
            mobile.skip_signal = False
            mobile.save()
            contact.phone_numbers.add(mobile)

        contact.skip_signal = False
        contact.save()


def new_or_existing_contact(row, tenant_id, optional_in_upload):
    """
    Determine if Lily needs to create a new contact with the given row or that it should update a current contact.
    """
    account = None
    email_address = None
    formatted_phone_number = None

    first_name = row.get(u'first name')
    last_name = row.get(u'last name')

    if u'company name' in optional_in_upload and row.get(u'company name'):
        company_name = row.get(u'company name')
        try:
            account = Account.objects.get(name=company_name, tenant_id=tenant_id, is_deleted=False)
        except Account.DoesNotExist:
            pass

    if u'email address' in optional_in_upload and row.get(u'email address'):
        email_address = row.get(u'email address').lower()

    if u'phone number' in optional_in_upload and row.get(u'phone number'):
        formatted_phone_number = parse_phone_number(row.get(u'phone number'))

    # Regard as a existing contact when there is one in the database with the given name in combination with the
    # email address and / or phone number.
    qs = Contact.objects.filter(
        first_name=first_name,
        last_name=last_name,
        tenant_id=tenant_id,
        is_deleted=False
    )

    if account:
        qs = qs.filter(
            functions__account=account
        )

    if email_address and formatted_phone_number:
        qs = qs.filter(
            Q(email_addresses__email_address=email_address) | Q(phone_numbers__number=formatted_phone_number)
        )
    elif email_address:
        qs = qs.filter(email_addresses__email_address=email_address)
    elif formatted_phone_number:
        qs = qs.filter(phone_numbers__number=formatted_phone_number)

    contact = qs.first()

    if not contact:
        # There was no existing contact, so instantiate a new one.
        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            tenant_id=tenant_id
        )

    # Skip the signal at this moment, so on a rollback the instance isn't still in the search index.
    contact.skip_signal = True

    return contact


def import_account(row, tenant_id, headers):
    # The following set of fields should be present as headers in the uploaded file.
    required_fields = {u'company name'}
    # The following set of fields are optional.
    optional_fields = {u'website', u'email address', u'phone number', u'twitter', u'address', u'postal code', u'city'}

    # The following headers are present in the uploaded file.
    available_in_upload = set(headers)

    optional_in_upload = optional_fields & available_in_upload
    extra_in_upload = available_in_upload - (required_fields | optional_fields)

    company_name = row.get(u'company name')

    website = None
    email_address = None
    phone_number = None
    twitter = None
    address = None
    try:
        # Use atomic to rollback all intermediate database actions if an error occurs in just one of them.
        with transaction.atomic():
            description = ''
            # All the extra fields that are present in the upload are placed in the description field.
            for field in extra_in_upload:
                description += '{0}: {1}\n'.format(field, row.get(field))

            # Not using get_or_create() to make use of the skip_signal construction.
            try:
                account = Account.objects.get(name=company_name, tenant_id=tenant_id)
                if description:
                    new_description = '{0}\n{1}'.format(account.description.strip(), description)
                    account.description = new_description
                    account.skip_signal = True
                    account.save()
            except Account.DoesNotExist:
                account_status = AccountStatus.objects.get(name='Relation', tenant_id=tenant_id)
                account = Account(
                    name=company_name,
                    tenant_id=tenant_id,
                    status=account_status,
                    description=description
                )
                account.skip_signal = True
                account.save()

            if u'website' in optional_in_upload and row.get(u'website'):
                website = Website(
                    website=row.get(u'website'),
                    is_primary=True, account=account,
                    tenant_id=tenant_id
                )
                website.skip_signal = True
                website.save()

            if u'email address' in optional_in_upload and row.get(u'email address'):
                formatted_email_address = row.get(u'email address').lower()
                if not account.email_addresses.filter(email_address=formatted_email_address).exists():
                    email_address = EmailAddress(
                        email_address=formatted_email_address,
                        status=EmailAddress.PRIMARY_STATUS,
                        tenant_id=tenant_id
                    )
                    email_address.skip_signal = True
                    email_address.save()

            if u'phone number' in optional_in_upload and row.get(u'phone number'):
                formatted_phone_number = parse_phone_number(row.get(u'phone number'))
                phone_number = PhoneNumber(
                    number=formatted_phone_number,
                    tenant_id=tenant_id
                )
                phone_number.skip_signal = True
                phone_number.save()

            if u'twitter' in optional_in_upload and row.get(u'twitter'):
                twitter = SocialMedia(
                    name='twitter',
                    username=row.get(u'twitter'),
                    profile_url='https://twitter.com/{0}'.format(row.get(u'twitter')),
                    tenant_id=tenant_id
                )
                twitter.skip_signal = True
                twitter.save()

            # An Address consists of multiple, optional fields. So create or update the instance.
            if u'address' in optional_in_upload and row.get(u'address'):
                address = Address(
                    address=row.get(u'address'),
                    type='visiting',
                    tenant_id=tenant_id
                )
                address.skip_signal = True
                address.save()

            if u'postal code' in optional_in_upload and row.get(u'postal code'):
                if address:
                    address.postal_code = row.get(u'postal code')
                else:
                    address = Address(
                        postal_code=row.get(u'postal code'),
                        type='visiting',
                        tenant_id=tenant_id
                    )
                address.skip_signal = True
                address.save()

            if u'city' in optional_in_upload and row.get(u'city'):
                if address:
                    address.city = row.get(u'city')
                else:
                    address = Address(
                        city=row.get(u'city'),
                        type='visiting',
                        tenant_id=tenant_id
                    )
                address.skip_signal = True
                address.save()

    except Exception as e:
        # On an exception all database actions are rolled back. Because of the skip_signal=True no data is added to the
        # search index.
        logger.error(u'Import error {} for {}'.format(e, company_name))
    else:
        if website:
            website.skip_signal = False
            website.save()
            account.websites.add(website)
        if email_address:
            email_address.skip_signal = False
            email_address.save()
            account.email_addresses.add(email_address)
        if phone_number:
            phone_number.skip_signal = False
            phone_number.save()
            account.phone_numbers.add(phone_number)
        if twitter:
            twitter.skip_signal = False
            twitter.save()
            account.social_media.add(twitter)
        if address:
            address.skip_signal = False
            address.save()
            account.addresses.add(address)

        account.skip_signal = False
        account.save()
