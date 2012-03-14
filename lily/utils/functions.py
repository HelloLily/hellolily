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