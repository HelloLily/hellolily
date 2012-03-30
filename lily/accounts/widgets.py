
from django.forms.widgets import SelectMultiple
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape

class InputAndSelectMultiple(SelectMultiple):
    """
    An subclass of SelectMultiple to create option elements with the same value as text to support 
    input-and-choice javascript.
    """
    
    def __init__(self, attrs=None, preselected=(), choices=()):
        super(InputAndSelectMultiple, self).__init__(attrs, choices)
        
        # TODO: handle preselected values 
    
    def render_option(self, selected_choices, option_value, option_label):
        """
        Overloading super().render_option() to print option_label twice (as text and value).
        """
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        return u'<option value="%s"%s>%s</option>' % (
            conditional_escape(force_unicode(option_label)), selected_html,
            conditional_escape(force_unicode(option_label)))