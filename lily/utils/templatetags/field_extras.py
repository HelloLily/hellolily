from django.forms.fields import ChoiceField, FileField
from django import template
register = template.Library()

# Code below found at django ticket #10427 https://code.djangoproject.com/ticket/10427
# According to the comments it should be fixed, but it doesn't seem to work in 1.3 or 1.4
# Added functionality: conversion to integer to be able to display the display value after posting
# a form (original int then turns into unicode).  

@register.filter(name='field_value')
def field_value(field):
    """ 
    Returns the value for this BoundField, as rendered in widgets. 
    """ 
    if field.form.is_bound:
        # Return posted value
        if isinstance(field.field, FileField) and field.data is None: 
            val = field.form.initial.get(field.name, field.field.initial) 
        else: 
            val = field.data 
    else:
        # Return initital value
        val = field.form.initial.get(field.name, field.field.initial)
        if callable(val):
            val = val()
    # Return empty string if nothing was found rather than None
    if val is None:
        val = ''
    return val

@register.filter(name='display_value')
def display_value(field): 
    """ 
    Returns the displayed value for this BoundField, as rendered in widgets. 
    """ 
    # Find the actual value
    value = field_value(field)
    # Try making an integer of it (it's unicode on post)
    try:
        value = int(value)
    except:
        pass
    # If it's a ChoiceField, try finding the display value
    if isinstance(field.field, ChoiceField): 
        for (val, desc) in field.field.choices: 
            if val == value: 
                return desc 
    return value


