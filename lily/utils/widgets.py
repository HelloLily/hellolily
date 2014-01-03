from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.forms.models import model_to_dict
from django.forms.widgets import Select, TextInput
from django.utils import simplejson, translation
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
        extra_attrs.update({
            'data-choices': ','.join(self.choices),
        })

        if 'class' not in kwargs:
            extra_attrs.update({
                'class': 'tags'
            })

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


class DatePicker(DateTimePicker):
    """
    Our version of a DatePicker based on bootstrap3_datetime's DateTimePicker.
    """
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (
        ('dd', r'%d'),  # Day of the month as a zero-padded decimal number
        ('MM', r'%B'),  # Month as locale's full name
        ('M', r'%b'),  # Month as locale's abbreviated name
        ('mm', r'%m'),  # Month as a zero-padded decimal number
        ('yyyy', r'%Y'),  # Year with century as a decimal number
        ('yy', r'%y'),  # Year without century as a zero-padded decimal number
    )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format

    html_template = '''
        <div%(div_attrs)s>
            <input%(input_attrs)s/>
            <span class="input-group-btn">
                <button class="btn default" type="button"><i%(icon_attrs)s></i></button>
            </span>
        </div>'''

    js_template = '''
        <script>
            $(function() {
                $("#%(picker_id)s").datepicker(%(options)s);
            });
        </script>'''

    def __init__(self, attrs=None, format=None, options=None, div_attrs=None, icon_attrs=None):
        if not icon_attrs:
            icon_attrs = {'class': 'icon-calendar'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        super(DatePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if options == False:  # datetimepicker will not be initalized only when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            self.options['language'] = translation.get_language()
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)
