from django.forms.widgets import Select
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape, escape


priority_css_class_mapping = {
    '0': 'green',
    '1': 'yellow',
    '2': 'orange',
    '3': 'red',
}


class PrioritySelect(Select):
    """
    Widget to render specific css classes on the option elements for this select.
    """
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        selected_html += ' class="i-16 i-tag %s"' % priority_css_class_mapping.get(option_value, '') if len(option_value) > 0 else ''
        return u'<option value="%s"%s>%s</option>' % (
            escape(option_value), selected_html,
            conditional_escape(force_unicode(option_label))
        )