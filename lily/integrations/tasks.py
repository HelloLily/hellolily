import logging

from celery.task import task
from django.db import transaction

from lily.accounts.models import Account, AccountStatus
from lily.contacts.models import Contact, Function
from lily.tenant.models import Tenant
from lily.utils.functions import send_get_request
from lily.utils.models.models import Address, EmailAddress, PhoneNumber

from .credentials import get_credentials

logger = logging.getLogger(__name__)


@task(name='import_moneybird_contacts')
def import_moneybird_contacts(tenant_id):
    importing = True
    page = 1

    tenant = Tenant.objects.get(pk=tenant_id)
    # Can't retreive tenant from request here, so get the tenant.
    credentials = get_credentials('moneybird', tenant)

    administration_id = credentials.integration_context.get('administration_id')

    # New tenants have this account status, but older tenants might not.
    account_status, status_created = AccountStatus.objects.get_or_create(name='Customer', tenant=tenant)

    base_url = 'https://moneybird.com/api/v2/%s/contacts?page=%s&per_page=100'

    while importing:
        url = base_url % (administration_id, page)
        response = send_get_request(url, credentials)

        data = response.json()

        if data:
            for contact_data in data:
                # For every field we want to fill we do the following:
                # 1. Setup a dict with the information.
                # 2. Retrieve all objects with that info.
                # 3. If no object exists, create a new one (and add to set for related objects).
                try:
                    with transaction.atomic():
                        contact = None
                        first_name = contact_data.get('firstname')
                        last_name = contact_data.get('lastname', '')

                        if first_name:
                            contact_dict = {
                                'first_name': first_name,
                                'last_name': last_name,
                                'tenant': tenant,
                                'is_deleted': False
                            }
                            # Since we have the possibility to resync we want to update
                            # contacts that might already exist.
                            contact = Contact.objects.filter(**contact_dict).last()

                            if not contact:
                                contact = Contact.objects.create(**contact_dict)

                        company = contact_data.get('company_name')

                        if company:
                            account_dict = {
                                'name': company,
                                'status': account_status,
                                'tenant': tenant,
                                'is_deleted': False
                            }
                            account = Account.objects.filter(**account_dict).last()

                            if not account:
                                account = Account.objects.create(**account_dict)

                            if contact:
                                # Contacts and accounts are linked through functions.
                                Function.objects.get_or_create(account=account, contact=contact)

                        if contact:
                            # Save all contact info to the contact if there is one.
                            contact_object = contact
                        else:
                            # Otherwise use the account.
                            contact_object = account

                        invoices_email = contact_data.get('send_invoices_to_email')
                        estimates_email = contact_data.get('send_estimates_to_email')
                        phone = contact_data.get('phone')
                        address = contact_data.get('address1')
                        alternate_address = contact_data.get('address2')

                        if invoices_email:
                            invoices_email_dict = {
                                'email_address': invoices_email,
                                'tenant': tenant,
                            }
                            invoices_email_address = contact_object.email_addresses.filter(**invoices_email_dict)

                            if not invoices_email_address.last():
                                invoices_email_address = EmailAddress.objects.create(**invoices_email_dict)
                                contact_object.email_addresses.add(invoices_email_address)

                        if estimates_email and not invoices_email == estimates_email:
                            # No point in adding two of the same email addresses.
                            estimates_email_dict = {
                                'email_address': estimates_email,
                                'tenant': tenant,
                            }
                            estimates_email_address = contact_object.email_addresses.filter(**estimates_email_dict)

                            if not estimates_email_address.last():
                                estimates_email_address = EmailAddress.objects.create(**estimates_email_dict)
                                contact_object.email_addresses.add(estimates_email_address)

                        if phone:
                            phone_number_dict = {
                                'number': phone,
                                'tenant': tenant,
                            }
                            phone_number = contact_object.phone_numbers.filter(**phone_number_dict).last()

                            if not phone_number:
                                phone_number = PhoneNumber.objects.create(**phone_number_dict)
                                contact_object.phone_numbers.add(phone_number)

                        if address:
                            postal_code = contact_data.get('zipcode')
                            city = contact_data.get('city')
                            country = contact_data.get('country')

                            address_dict = {
                                'address': address,
                                'postal_code': postal_code,
                                'city': city,
                                'country': country,
                                'tenant': tenant,
                            }

                            address = Address.objects.filter(**address_dict).last()

                            if not address:
                                address = Address.objects.create(**address_dict)
                                contact_object.addresses.add(address)

                            if alternate_address:
                                address_dict = ({
                                    'address': alternate_address,
                                    'country': country,
                                    'tenant': tenant,
                                })

                                alternate_address = Address.objects.filter(**address_dict).last()

                                if not alternate_address:
                                    alternate_address = Address.objects.create(**address_dict)
                                    contact_object.addresses.add(alternate_address)

                        contact_object.save()
                except Exception as e:
                    logger.error(e)

            # Increment the page so we can check for more contacts.
            page += 1
        else:
            importing = False
