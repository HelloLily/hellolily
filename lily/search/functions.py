from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.utils.functions import parse_phone_number


def search_number(tenant_id, number):
    """
    If the phone number belongs to an account, this returns the first account and all its contacts
    Else if the number belongs to a contact, this returns the first contact and all its accounts
    """
    phone_number = parse_phone_number(number)
    accounts = Account.objects.filter(phone_numbers__number=phone_number, is_deleted=False)
    contacts = Contact.objects.filter(phone_numbers__number=phone_number, is_deleted=False)

    accounts_result = []
    contacts_result = []

    if accounts:
        accounts_result = [accounts[0]]
    elif contacts:
        contacts_result = [contacts[0]]

    return {
        'data': {
            'accounts': accounts_result,
            'contacts': contacts_result,
        },
    }
