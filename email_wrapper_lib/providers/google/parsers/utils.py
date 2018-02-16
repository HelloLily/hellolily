from email._parseaddr import AddressList

import pytz
from email.utils import parsedate_tz, mktime_tz, formataddr

from datetime import datetime
from dateutil.parser import parse

from email_wrapper_lib.providers.exceptions import BatchRequestException


def parse_batch_response(callback, promise):
    def transform(request_id, data, exception):
        if exception:
            raise BatchRequestException(exception)
        else:
            callback(data, promise)

    return transform


def parse_date_string(data):
    # TODO: try to use the tuple in an easier way using time.mktime

    # Try it the most simple way.
    datetime_tuple = parsedate_tz(data)
    if datetime_tuple:
        return datetime.fromtimestamp(mktime_tz(datetime_tuple), pytz.UTC)
    else:
        return parse(data)


def parse_recipient_string(data):
    a = AddressList(data)

    return [{
        'name': recipient[0],
        'email_address': recipient[1],
        'raw_value': formataddr((recipient[0], recipient[1]))
    } for recipient in a.addresslist]


def parse_page(data):
    return data.get('nextPageToken', None)


def parse_deletion(data, status_code):  # TODO: status_code marked as unused, not passed by reference?
    # TODO: does this work for Google?
    status_code = data.status_code  # TODO: What happens to the status codes on the other parse methods? Lost?
    return status_code
