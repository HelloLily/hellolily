# Python imports
from datetime import datetime

# Django imports
from django import template
from django.template import defaultfilters
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter
def naturaldatetime(value, arg='d b'):
    """
    For date values that are tomorrow, today or yesterday compared to
    present day returns representing string. Otherwise, returns a string
    formatted according to settings.DATE_FORMAT.
    """
    if not type(value) is datetime:
        return value
    
    tzinfo = getattr(value, 'tzinfo', None)
    today = datetime.now(tzinfo).date()
    delta = value.date() - today
    
    if delta.days == 0: #Check if today
        return value.strftime('%H:%M')
    elif delta.days == 1: #Check if tomorrow
        return _(u'tomorrow')
    elif delta.days == -1: #Check if yesterday
        return _(u'yesterday')
    elif (delta.days > 365) or (delta.days < -365): #Check if not within the same year
        return defaultfilters.date(value, 'd-m-Y')
    return defaultfilters.date(value, arg) #Return 'day month'