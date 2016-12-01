import json

from bootstrap3_datetime.widgets import DateTimePicker
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.forms.formsets import BaseFormSet
from django.forms.widgets import TextInput, Widget, RadioFieldRenderer, Textarea
from django.forms.utils import flatatt
from django.utils import translation
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


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
            icon_attrs = {'class': 'fa fa-calendar'}
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
        if options is False:  # datetimepicker will not be initalized only when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            self.options['language'] = translation.get_language()
            if not self.options.get('weekStart'):
                self.options['weekStart'] = 1
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)


class LilyDateTimePicker(DatePicker):
    """
    Modified DatePicker to support times. Note: It uses bootstrap-datetimepicker
    plugin instead of bootstrap-datepicker.
    """
    format_map = (
        ('dd', r'%d'),
        ('mm', r'%m'),
        ('yyyy', r'%Y'),
        ('hh', r'%H'),
        ('ii', r'%M'),
    )

    js_template = '''
        <script>
            $(function() {
                $('#%(picker_id)s input').datetimepicker(%(options)s);
                $('#%(picker_id)s button').click(function() {
                    $("#%(picker_id)s input").datetimepicker('show');
                })
            });
        </script>'''


class AddonTextInput(TextInput):
    """
    Creates a text input with an addon (icon)
    """
    def __init__(self, attrs=None, div_attrs=None, button_attrs=None, icon_attrs=None):
        if 'is_button' not in icon_attrs.keys() or icon_attrs.get('is_button'):
            span = '''
                <span class="input-group-btn">
                    <button%(button_attrs)s><i%(icon_attrs)s></i></button>
                </span>'''
        else:
            span = '''
                <span class="input-group-addon">
                   <i%(icon_attrs)s></i>
                </span>'''

        if not icon_attrs.get('position') or icon_attrs.get('position') == 'right':
            self.html_template = '''
                <div%(div_attrs)s>
                    <input%(input_attrs)s/>
                ''' + \
                span + \
                '''</div>'''
        else:
            self.html_template = '''
                <div%(div_attrs)s>''' + \
                span + \
                '''<input%(input_attrs)s/>
                </div>'''

            if icon_attrs.get('class'):
                icon_attrs = {'class': icon_attrs.get('class')}

        button_attrs = {} if not button_attrs else button_attrs
        if not button_attrs.get('class'):
            button_attrs.update({'class': 'btn default'})
        if not button_attrs.get('type'):
            button_attrs.update({'type': 'button'})
        if not button_attrs.get('data-loading-text'):
            button_attrs.update({'data-loading-text': 'loading...'})
        if not button_attrs.get('autocomplete'):
            button_attrs.update({'autocomplete': 'off'})

        if not div_attrs:
            div_attrs = {'class': 'input-group'}

        super(AddonTextInput, self).__init__(attrs)

        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.button_attrs = button_attrs and button_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        input_attrs = self.build_attrs(attrs, type=self.input_type, name=name)

        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self._format_value(value))
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])

        div_attrs = dict([(key, conditional_escape(val)) for key, val in self.div_attrs.items()])
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        button_attrs = dict([(key, conditional_escape(val)) for key, val in self.button_attrs.items()])

        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         button_attrs=flatatt(button_attrs),
                                         icon_attrs=flatatt(icon_attrs))

        return mark_safe(force_text(html))


class BootstrapRadioFieldRenderer(RadioFieldRenderer):
    """
    An object used by RadioSelect to enable customization of radio widgets.
    """
    def render(self):
        """
        Outputs a bootstrap button group for this set of radio fields.
        """
        buttons_html = mark_safe('')

        # Render each radioinput bootstrap-like.
        for choice in self:
            buttons_html += u'''<label class="btn btn-primary %(is_active)s">%(tag)s %(label)s</label>''' % {
                'is_active': ('active' if choice.is_checked() else ''),
                'tag': choice.tag(),
                'label': choice.choice_label,
            }

        return mark_safe(u'''<div class="btn-group radio-btns" data-toggle="buttons">%s</div>''' % buttons_html)


class FormSetWidget(Widget):
    choices = None

    def __init__(self, queryset=None, form_attrs=None, attrs=None):
        super(FormSetWidget, self).__init__(attrs)

        self.queryset = queryset
        self.form_attrs = form_attrs

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)

        if self.form_attrs:
            for form_attr, form_value in self.form_attrs.items():
                setattr(final_attrs['formset_class'].form, form_attr, form_value)

        value = value or []
        if not isinstance(value, BaseFormSet):
            if isinstance(value, QuerySet):
                queryset = value  # most likely initial data
            else:
                queryset = self.queryset.filter(pk__in=value)
            value = final_attrs['formset_class'](prefix=name, queryset=queryset)

        return render_to_string(final_attrs['template'], {
            'formset': value,
        })

    def value_from_datadict(self, data, files, name):
        return self.attrs['formset_class'](data, files, prefix=name)


class AjaxSelect2Widget(Widget):
    """
    Widget that renders a hidden input that can be turned to an Select2 select.

    Attributes:
        queryset (instance): QuerySet instance
        url (str): url for ajax call from Select2
        filter_on (str): id of field that Select2 adds as filter with ajax call
    """
    def __init__(self, model, url, tags=None, attrs=None, **kwargs):
        super(AjaxSelect2Widget, self).__init__(attrs)
        self.model = model
        self.url = url
        self.tags = tags
        self.filter_on = kwargs.get('filter_on', None)

    def render(self, name, value, attrs=None, *args):
        final_attrs = self.build_attrs(attrs, name=name)

        if self.tags:
            final_attrs['data-tags'] = True

        if hasattr(self, 'data'):
            # This is an ugly hack to pass the field's initial value to the select2,
            # in case we got a multi-select version of select2.
            initial = []
            for data in self.data:
                initial.append({'id': data.pk, 'text': data.name})

            final_attrs['data-initial'] = json.dumps(initial)
        elif isinstance(value, list):
            # This is to make sure the recipients input gets populated with recipients
            initial = []
            for data in value:
                initial.append({'id': data['id'], 'text': data['text']})

            final_attrs['data-initial'] = json.dumps(initial)
            final_attrs['data-tags'] = True
        else:
            # Add initial value
            if value:
                final_attrs['value'] = value
                if isinstance(value, basestring):
                    selected_text = value
                else:
                    try:
                        selected_text = str(self.model.objects.get(pk=value))
                    except ObjectDoesNotExist:
                        selected_text = ''

                final_attrs['data-selected-text'] = selected_text

        final_attrs['data-ajax-url'] = self.url

        # Multi-select version doesn't have a choices field, but uses data-initial.
        if hasattr(self, 'choices') and not isinstance(self.choices, list):
            final_attrs['placeholder'] = self.choices.field.empty_label

        if self.filter_on:
            final_attrs['data-filter-on'] = self.filter_on

        # Class to activate ajaxselect2
        class_attrs = final_attrs.get('class', None)
        if class_attrs:
            class_attrs += ' select2ajax'
        else:
            class_attrs = 'select2ajax'
        final_attrs['class'] = class_attrs

        return mark_safe('<input type="hidden"%s>' % flatatt(final_attrs))


class Wysihtml5Input(Textarea):
    """
    Widget for displaying the textarea as wysihtml5 input
    """

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'inbox-editor inbox-wysihtml5 form-control'
        }
        if attrs:
            default_attrs.update(attrs)
        super(Wysihtml5Input, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return render_to_string('utils/wysihtml5.html', {
            'name': name,
            'value': value,
            'attrs': final_attrs,
        })
