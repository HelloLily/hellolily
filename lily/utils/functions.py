from django import forms
from django.contrib import messages
import re
import string


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
def uniquify (sequence, function=None):
    """
    Remove non-unique items from given sequence. Redirect call to _uniquify for the actual
    uniquifying.
    
    function can for example be lambda x: x.lower() to also remove items that are actually the same 
    except for lettercase ['a', 'A'], which will prevent the latter from joining the result list.
    """
    return list(_uniquify (sequence, function))
def _uniquify (sequence, function=None):
    """
    The function that actually uniquifies the sequence.
    
    One of the fastest ways to uniquify a sequence according to http://www.peterbe.com/plog/uniqifiers-benchmark
    with full support of also non-hashable sequence items.
    """
    seen = set()
    if function is None:
        for x in sequence:
            if x in seen:
                continue
            seen.add(x)
            yield x
    else:
        for x in sequence:
            x = function(x)
            if x in seen:
                continue
            seen.add(x)
            yield x
    
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

def dummy_function(x, y=None):
    return y

def import_from_string(string_name):
    """
    Given a string like 'module.submodule.name' which refers to a function or class, return that 
    function so it can be called (or the class)
    
    source: http://www.technomancy.org/python/converting-string-to-function/
    """
    # Split the string_name into 2, the module that it's in, and func_name, the function itself
    mod_name, func_name = string_name.rsplit(".", 1)

    mod = __import__(mod_name)
    # ``__import__`` only gives us the top level module, i.e. ``module``, so 'walk down the tree' getattr'ing each submodule.
    # from http://docs.python.org/faq/programming.html?highlight=importlib#import-x-y-z-returns-module-x-how-do-i-get-z
    for i in mod_name.split(".")[1:]:
        mod = getattr(mod, i)

    # Now that we have a reference to ``module.submodule``, ``func_name`` is available as an attribute to that, so return it.
    return getattr(mod, func_name)

from lily.settings import TENANT_MIXIN
get_tenant_mixin = import_from_string(TENANT_MIXIN)
