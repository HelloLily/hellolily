
from django.forms.util import flatatt
from django.forms.widgets import SelectMultiple
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

class InputAndSelectMultiple(SelectMultiple):
    """
    An subclass of SelectMultiple to create option elements with the same value as text to support 
    input-and-choice javascript.
    """
    
    def __init__(self, attrs=None, preselected=(), choices=()):
        super(InputAndSelectMultiple, self).__init__(attrs, choices)
        
        # an array for choices that don't exist in the database yet
        self.new_choices = []
    
    def value_from_datadict(self, data, files, name):
        """
        Overloading super().value_from_datadict to temporarily save options that have been 
        submitted but don't in the database yet. This list of options will be used in self.render()
        to expand on the list of options that exist in the database.
        """
        choices = super(InputAndSelectMultiple, self).value_from_datadict(data, files, name)
        
        # Extract option_label from self.choices queryset
        existing_choices = []
        for choice in self.choices:
            existing_choices.append(choice[1])
        
        # Filter already existing choices from choices
        self.new_choices = filter(lambda x:x not in existing_choices, choices)
        
        return choices
    
    def render(self, name, value, attrs=None, choices=()):
        """
        Overloading super().render to inject options extracted from the POST data to the choices 
        list so these options are rendered when the form is invalid.
        """
        # Expand choices with options that haven't seen the light in the database yet
        choices = list(choices)
        for choice in self.new_choices:
            choices.append([choice, choice])
        # Convert back to tuple
        choices = tuple(choices)
        
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select multiple="multiple"%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe(u'\n'.join(output))
    
    def render_option(self, selected_choices, option_value, option_label):
        """
        Overloading super().render_option to print option_label twice (as text and value) and
        to use option_label to check if an option has been selected.
        """
        option_value = force_unicode(option_value)
        if option_label in selected_choices:
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        return u'<option value="%s"%s>%s</option>' % (
            conditional_escape(force_unicode(option_label)), selected_html,
            conditional_escape(force_unicode(option_label)))