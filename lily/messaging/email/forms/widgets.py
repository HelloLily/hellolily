import json

from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.forms.widgets import ClearableFileInput, CheckboxInput, Select
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe

from lily.messaging.email.models import EmailProvider
from lily.messaging.email.utils import get_attachment_filename_from_url


class EmailAttachmentWidget(ClearableFileInput):
    template_with_initial = u'%(initial)s'

    # template_with_clear = u'%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial

            url = reverse('email_attachment_proxy_view', kwargs={'pk': 5, 'path': value.url})
            substitutions['initial'] = (u'<a href="%s">%s</a>'
                                        % (escape(url),
                                           escape(get_attachment_filename_from_url(force_unicode(value)))))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)


class EmailProviderSelect(Select):
    """
    Subclassing to enable filling out the form with attributes of an EmailProvider instance.
    These attributes will be JSON serialized as a html5 data attribute on the option elements.
    """
    def render_option(self, selected_choices, option_value, option_label):
        json_html = u''
        if isinstance(option_value, EmailProvider):
            json_html = u' data-serialized="%s"' % escape(json.dumps(model_to_dict(option_value, exclude=['id', 'tenant', 'name'])))
            option_value = option_value.pk
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, json_html,
            conditional_escape(force_unicode(option_label)))
