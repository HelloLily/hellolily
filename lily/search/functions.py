from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.utils.functions import parse_phone_number


def search_number(tenant_id, number, return_related=True):
    """
    If the phone number belongs to an account, this returns the first account and all its contacts
    Else if the number belongs to a contact, this returns the first contact and all its accounts
    """
    # TODO LILY-2785 LILY-2786: This function should not exist.
    phone_number = parse_phone_number(number)
    accounts = Account.objects.filter(phone_numbers__number=phone_number, is_deleted=False)
    contacts = Contact.objects.filter(phone_numbers__number=phone_number, is_deleted=False)

    accounts_result = []
    contacts_result = []

    if accounts:
        accounts_result = [accounts[0]]

        if return_related:
            contacts_result = accounts[0].contacts.filter(is_deleted=False)
    elif contacts:
        contacts_result = [contacts[0]]

        if return_related:
            accounts_result = contacts[0].accounts.filter(is_deleted=False)

    return {
        'data': {
            'accounts': accounts_result,
            'contacts': contacts_result,
        },
    }
