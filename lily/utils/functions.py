from django import forms

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