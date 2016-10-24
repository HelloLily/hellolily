import re
import urlparse
from time import time

import anyjson
import requests
from django import forms

from lily.settings import settings


def autostrip(cls):
    """
    Add functionality to forms for stripping whitespace from CharFields (and descendants except
    those with PasswordInput widget).

    This method is the implementation from http://djangosnippets.org/snippets/956/
    We added the exception for fields with a PasswordInput widget.
    """

    fields = [(key, value) for key, value in cls.base_fields.iteritems()
              if isinstance(value, forms.CharField) and not isinstance(value.widget, forms.PasswordInput)]
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
    Parse an address string and return street, number and complement.
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


def is_int(string):
    """
    Helper function to check if string is int.

    Arguments:
        string (str): string to check

    Returns:
        Boolean: True if string is int.
    """
    try:
        int(string)
        return True
    except (TypeError, ValueError):
        return False


def clean_website(website):
    # Empty website, don't clean it
    if website != 'http://':
        website = website.strip().strip('/')

        if not urlparse.urlparse(website).scheme:
            website = 'http://' + website

        parse_result = urlparse.urlparse(website)
        # Only lowercase the domain part of the url.
        # Tuples are immutable, so use _replace to set the new value.
        parse_result = parse_result._replace(netloc=parse_result.netloc.lower())

        website = urlparse.urlunparse(parse_result)

    return website


def post_intercom_event(event_name, user_id):
    """
    Sends a request to Intercom to track the given event.

    Args:
        event_name (str): Name of the event that we want to track.
        user_id (int): ID of the Lily user.

    Returns:
        response (Response): Object containing the response information.
    """
    if not settings.DEBUG:
        payload = {
            'event_name': event_name,
            'user_id': user_id,
            'created_at': int(time())
        }

        response = requests.post(
            url='https://api.intercom.io/events',
            data=anyjson.serialize(payload),
            auth=(settings.INTERCOM_APP_ID, settings.INTERCOM_KEY),
            headers={'Content-Type': 'application/json'}
        )

        return response
    return None


def send_get_request(url, credentials):
    headers = {
        'Authorization': 'Bearer %s' % credentials.access_token
    }

    response = requests.get(url, headers=headers)

    return response


def send_post_request(url, credentials, params):
    headers = {
        'Authorization': 'Bearer %s' % credentials.access_token
    }

    response = requests.post(url, headers=headers, json=params)

    return response
