import operator
import re
from itertools import chain

from django import forms
from django.contrib import messages
from django.db.models import Q
from python_imap.folder import ALLMAIL, SENT, INBOX, IMPORTANT


def autostrip(cls):
    """
    Add functionality to forms for stripping whitespace from CharFields (and descendants except
    those with PasswordInput widget).

    This method is the implementation from http://djangosnippets.org/snippets/956/
    We added the exception for fields with a PasswordInput widget.
    """

    fields = [(key, value) for key, value in cls.base_fields.iteritems() if isinstance(value, forms.CharField) and not isinstance(value.widget, forms.PasswordInput)]
    for field_name, field_object in fields:
        def get_clean_func(original_clean):
            return lambda value: original_clean(value and value.strip())
        clean_func = get_clean_func(getattr(field_object, 'clean'))
        setattr(field_object, 'clean', clean_func)
    return cls


# TODO: build testcase
def uniquify(sequence, function=None, filter=None):
    """
    Remove non-unique items from given sequence. Redirect call to _uniquify for the actual
    uniquifying.

    function can for example be lambda x: x.lower() to also remove items that are actually the same
    except for lettercase ['a', 'A'], which will prevent the latter from joining the result list.
    """
    return list(_uniquify(sequence, function, filter))


def _uniquify(sequence, function=None, filter=None):
    """
    Function: manipulate what is being returned.
    Filter: manipulate what is being compared.

    One of the fastest ways to uniquify a sequence according to http://www.peterbe.com/plog/uniqifiers-benchmark
    with full support of also non-hashable sequence items.
    """
    seen = set()
    if filter is None:
        for x in sequence:
            if x in seen:
                continue
            seen.add(x)
            yield x if function is None else function(x)
    else:
        for x in sequence:
            x_mod = filter(x)
            if x_mod in seen:
                continue
            seen.add(x_mod)
            yield x if function is None else function(x)


def is_ajax(request):
    """
    Return True if the request is for the AJAX version of a view.
    """
    return request.is_ajax() or 'xhr' in request.GET


def clear_messages(request):
    """
    Clear messages for given request.
    """
    storage = messages.get_messages(request)
    storage.used = True


def parse_phone_number(raw_number):
    number = filter(type(raw_number).isdigit, raw_number)

    # Replace starting digits
    if number[:3] == '310':
        number = number.replace('310', '31', 1)
    if number[:2] == '06':
        number = number.replace('06', '316', 1)
    if number[:1] == '0':
        number = number.replace('0', '31', 1)

    if len(number) > 0:
        number = '+' + number

    return number


def parse_address(address):
    """
    Parse an address string and return street, number and complement
    """
    street = None
    street_number = None
    complement = None
    try:
        if len(address) > 0:
            match = re.search('\d', address)
            if match:
                number_pos = match.start()
                street = address[:number_pos].strip()
                match = re.search('[^\d]', address[number_pos:])
                if match:
                    complement_pos = match.start()
                    street_number = address[number_pos:][:complement_pos].strip()

                    match = re.search('[a-zA-Z]', address[number_pos:][complement_pos:])
                    if match:
                        actual_complement_pos = match.start()
                        complement = address[number_pos:][complement_pos:][actual_complement_pos:].strip()
                    else:
                        complement = address[number_pos:][complement_pos:].strip()
                else:
                    street_number = address[number_pos:].strip()
            else:
                street = address
    except:
        pass

    return street, street_number, complement


def flatten(input):
    """
    Flatten the input so only alphanumeric characters remain.
    """
    pattern = re.compile('[\W_]+')
    return pattern.sub('', re.escape(input)).lower()


def dummy_function(x, y=None):
    return x, y


def get_emails_for_email_addresses(email_addresses_list):
    """
    Finds all emails with headers that have one of the given email_addresses.

    Args:
        list of strings: strings with email addresses.

    Returns:
        QuerySet of EmailMessages.
    """
    # Prevent circular import.
    from lily.messaging.email.models import EmailAddressHeader, EmailMessage

    # Get the message id's first.
    filter_list = [Q(value=email.email_address) for email in email_addresses_list]
    message_ids = EmailAddressHeader.objects.filter(
        Q(name__in=['To', 'From', 'CC', 'Delivered-To', 'Sender']) &
        reduce(operator.or_, filter_list)
    ).values_list('message_id', flat=True).distinct()
    message_ids = list(message_ids)

    # Get all the email messages with the collected id's.
    # TODO: replace _default_manager with objects when Polymorphic works.
    email_messages = EmailMessage._default_manager.filter(id__in=message_ids, folder_identifier__in=[ALLMAIL, SENT, INBOX, IMPORTANT])
    # return email_messages.order_by('-sort_by_date', 'message_identifier').distinct('sort_by_date', 'message_identifier')
    return email_messages.order_by('-sort_by_date', 'message_identifier').distinct('message_identifier', 'sort_by_date')


def combine_notes_qs_email_qs(notes_qs, email_qs, objects_size):
    """
    Gets a notes_qs and and an email_qs and combines it to one object_list.

    Sorts the list on sort_by_date and limits the query to objects_size.

    Args:
        notes_qs: QuerySet of Notes.
        email_qs: QuerySet of EmailMessages.
        objects_size (int): Maximum size of returned object_list.

    Returns:
        QuerySet with objects sorted by date and limited by objects_size and
        Boolean if there are more results than currently shown.
    """
    # Limit the maximum amount of objects by object_size.
    notes_qs = notes_qs.order_by('-sort_by_date')[:objects_size + 1]
    email_qs = email_qs[:objects_size + 1]

    # Combine qs_one and qs_two into one object_list.
    object_list = sorted(
        chain(notes_qs, email_qs),
        key=lambda instance: instance.sort_by_date,
        reverse=True,
    )

    paged_object_list = object_list[:objects_size]
    show_more = len(object_list) > objects_size
    return paged_object_list, show_more
