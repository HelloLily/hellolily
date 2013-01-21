from datetime import datetime

from dateutil.tz import gettz, tzutc
from dateutil.parser import parse
from django import template
from django.conf import settings
register = template.Library()


@register.filter(name='pretty_datetime')
def pretty_datetime(time, format=None):
    """
    Returns a string telling how long ago datetime differs from now or format
    it accordingly. Time is an UTC datetime.
    """
    # Convert to utc
    if isinstance(time, basestring):
        parsed_time = parse(time)
        parsed_time.tzinfo._name = None  # clear tzname to rely solely on the offset (not all tznames are supported)
        utc_time = parsed_time.astimezone(tzutc())
    elif isinstance(time, datetime):
        utc_time = time.astimezone(tzutc())
    else:
        return None

    # Convert to local
    localized_time = utc_time.astimezone(gettz(settings.TIME_ZONE))
    localized_now = datetime.now(tzutc()).astimezone(gettz(settings.TIME_ZONE))

    if isinstance(format, basestring):
        return datetime.strftime(localized_time, format)

    # Format based on local times
    if localized_now.toordinal() - localized_time.toordinal() == 0:  # same day
        return datetime.strftime(localized_time, '%H:%M')
    elif localized_now.year != localized_time.year:
        return datetime.strftime(localized_time, '%d-%m-%y')
    else:
        return datetime.strftime(localized_time, '%d-%b.')
