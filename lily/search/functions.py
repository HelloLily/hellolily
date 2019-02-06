from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.utils.functions import parse_phone_number


def search_number(tenant_id, number):
    """
    Return the first account the number belongs to, otherwise if there is, return the first contact with that number.
    """
    contact = None
    # TODO LILY-2785 LILY-2786: This function should not exist.
    phone_number = parse_phone_number(number)

    account = Account.objects.filter(
        phone_numbers__number=phone_number,
        tenant=tenant_id,
        is_deleted=False
    ).only('id', 'name').first()

    if not account:
        contact = Contact.objects.filter(
            phone_numbers__number=phone_number,
            tenant=tenant_id,
            is_deleted=False
        ).only('id', 'first_name', 'last_name').first()

    return account, contact
