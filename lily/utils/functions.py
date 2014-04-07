import re

from django import forms
from django.contrib import messages


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


def get_object_pks(object):
    """
    Get object_pks from POST info if not set
    """
    # PK already set
    if object.object_pks:
       return object.object_pks

    # retreive from POST data
    object_pks = object.request.POST.get('ids[]', None)
    if not object_pks:
       # no objects posted
       raise AttributeError("Generic Archive view %s must be called with "
                        "at least one object pk."
                        % object.__class__.__name__)
    elif object_pks.find(',') != -1:
       # multi objects
       object.object_pks = object_pks.split(',')
    else:
       # single object
       object.object_pks = [object_pks]

    return object.object_pks


def dummy_function(x, y=None):
    return x, y


