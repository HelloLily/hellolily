import re
import urlparse
import datetime

from time import time

import anyjson
import phonenumbers
import requests
from django import forms
from django.conf import settings
from phonenumbers import geocoder
import pycountry
from requests_futures.sessions import FuturesSession
from lily.tenant.middleware import get_current_user


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


def format_phone_number(number, country_code=None, international=False):
    if international:
        # Parse phone number in E164 standard which is INTERNATIONAL format but with no formatting (spaces, separating
        # symbols) applied, e.g. "+41446681800".
        number_format = phonenumbers.PhoneNumberFormat.E164
    else:
        # Parse phone number in NATIONAL standard which includes spaces, e.g. "044 668 1800".
        number_format = phonenumbers.PhoneNumberFormat.NATIONAL

    try:
        parsed_number = phonenumbers.parse(number, country_code)
    except:
        parsed_number = ''
    else:
        # Get the text representation of the phone number using the provided format and remove optional spaces.
        parsed_number = phonenumbers.format_number(parsed_number, number_format).replace(' ', '')

    return parsed_number


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
    if not any([settings.DEBUG, settings.TESTING]):
        payload = {
            'event_name': event_name,
            'user_id': user_id,
            'created_at': int(time())
        }

        response = requests.post(
            url='https://api.intercom.io/events',
            data=anyjson.serialize(payload),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % settings.INTERCOM_KEY,
            }
        )

        return response
    return None


def send_get_request(url, credentials):
    """
    Sends a GET request to the given url.

    Args:
        url (str): The url to call.
        credentials (obj): Object containing any authentication credentials.

    Returns:
        response (Response): Object containing the response information.
    """
    headers = {
        'Authorization': 'Bearer %s' % credentials.access_token
    }

    response = requests.get(url, headers=headers)

    return response


def send_post_request(url, credentials, params, patch=False, async_request=False):
    """
    Sends a POST request to the given url.

    Args:
        url (str): The url to call.
        credentials (IntegrationCredentials): Object containing any authentication credentials.
        params (dict): The data to be sent.

    Returns:
        response (Response): Object containing the response information. If the async_request
          option is used then returns an Future object instead. In this case the Response object
          can be got by calling response.result() for the returned value.
    """
    headers = {
        'Authorization': 'Bearer %s' % credentials.access_token
    }

    if async_request:
        session = FuturesSession()
        if patch:
            response = session.patch(url, headers=headers, json=params)
        else:
            response = session.post(url, headers=headers, json=params)
    else:
        if patch:
            response = requests.patch(url, headers=headers, json=params)
        else:
            response = requests.post(url, headers=headers, json=params)

    return response


def add_business_days(days_to_add, date=None):
    """
    Keep adding days to the given date while skipping weekends.

    Args:
        days_to_add (int): The number of days to add.
        date (date, optional): The date to add days to.

    Returns:
        date: The date with business days added to it.
    """
    if not date:
        date = datetime.datetime.utcnow().date()

    while days_to_add > 0:
        date += datetime.timedelta(days=1)
        weekday = date.weekday()

        if weekday >= 5:
            # Skip Saturday (5) and Sunday (6).
            continue
        days_to_add -= 1

    return date


def has_required_tier(required_tier, tenant=None):
    """
    Check if the current payment plan has access to the feature.
    This is done by comparing the tenant's current tier with the required tier.

    Args:
        required_tier (int): The minimum required tier to access the feature.

    Returns:
        (boolean): Whether or not the tier requirement is met.
    """
    if not tenant:
        user = get_current_user()
        tenant = user.tenant

    if settings.BILLING_ENABLED:
        current_tier = tenant.billing.plan.tier

        return current_tier >= required_tier
    else:
        # Billing isn't enable so always return true.
        return True


def guess_name_from_email(email):
    """
    Guess the name of a person using their email address.

    Example:
        email = 'some.name@domain.com'
        first_name, last_name = guess_name_from_email(email)

    Args:
        email (str): The email address to guess the name from.

    Returns:
        (list): A list of names.
    """

    full_name = email.split('@')[0]
    name = re.split('[._]', full_name)

    return name


def strip_protocol_from_url(url):
    """
    Return the passed url without the protocol and www.
    """
    url = url.strip()

    if url[:8] == 'https://':
        url = url[8:]
    if url[:7] == 'http://':
        url = url[7:]
    if url[:4] == 'www.':
        url = url[4:]

    return url


def get_country_by_phone_number(phone_number):
    """
    Get the English text representation of the country the number belongs to. Netherlands is used as fallback.
    """
    try:
        number_obj = phonenumbers.parse(phone_number, None)
        country = geocoder.country_name_for_number(number_obj, "en")
    except phonenumbers.NumberParseException:
        country = "Netherlands"

    return country


def get_country_code_by_country(country):
    """
    Get the country code (ISO 3166-1 alpha-2) by the country name provided. Use NL as a fallback.
    """
    try:
        country_code = pycountry.countries.get(name=country).alpha_2
    except KeyError:
        country_code = 'NL'

    return country_code
