from django import forms
from django.forms.models import model_to_dict
from django.forms.widgets import Select, SelectMultiple, TextInput
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape

from lily.messaging.email.models import EmailProvider


class JqueryPasswordInput(forms.PasswordInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(self._format_value(value))

        if 'class' in final_attrs:
            final_attrs['class'] = final_attrs['class'] + ' jquery-password'
        else:
            final_attrs.update({'class': 'jquery-password'})

        return super(JqueryPasswordInput, self).render(name, value, final_attrs)


class TagInput(TextInput):
    """
    The input used to select tags, seperate them by commas and put the entire tag list in a data attribute
    """

    def __init__(self, attrs=None, choices=()):
        super(TagInput, self).__init__(attrs)
        self.choices = list(choices)

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)

        return super(TagInput, self).render(name, value, final_attrs)

    def build_attrs(self, extra_attrs=None, **kwargs):
        extra_attrs = extra_attrs or {}
        extra_attrs.update({'data-choices': ",".join(self.choices)})
        return super(TagInput, self).build_attrs(extra_attrs=extra_attrs, **kwargs)


class EmailProviderSelect(Select):
    """
    Subclassing to enable filling out the form with attributes of an EmailProvider instance.
    These attributes will be JSON serialized as a html5 data attribute on the option elements.
    """
    def render_option(self, selected_choices, option_value, option_label):
        json_html = u''
        if isinstance(option_value, EmailProvider):
            json_html = u' data-serialized="%s"' % escape(simplejson.dumps(model_to_dict(option_value, exclude=['id', 'tenant', 'name'])))
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
