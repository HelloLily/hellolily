from bootstrap3_datetime.widgets import DateTimePicker
from django.db.models.query import QuerySet
from django.forms.formsets import BaseFormSet
from django.forms.widgets import TextInput, Widget, PasswordInput, RadioFieldRenderer
from django.forms.util import flatatt
from django.utils import translation
from django.utils.encoding import force_unicode, force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string


class JqueryPasswordInput(PasswordInput):
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


class AddonTextInput(TextInput):
    """
    Creates a text input with an addon (icon)
    """
    def __init__(self, attrs=None, div_attrs=None, button_attrs=None, icon_attrs=None):
        if not 'is_button' in icon_attrs.keys() or icon_attrs.get('is_button'):
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
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])  # python2.6 compatible

        div_attrs = dict([(key, conditional_escape(val)) for key, val in self.div_attrs.items()])  # python2.6 compatible
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        button_attrs = dict([(key, conditional_escape(val)) for key, val in self.button_attrs.items()])

        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         button_attrs=flatatt(button_attrs),
                                         icon_attrs=flatatt(icon_attrs))

        return mark_safe(force_text(html))


class ShowHideWidget(Widget):
    """
    Widget that adds functionality to toggle the visibility of a form input.

    Acts as a wrapper and passes all calls to another widget instance.
    """
    _widget = None

    def __init__(self, widget):
        self._widget = widget

    def __getattr__(self, name):
        return getattr(self._widget, name)

    def __setattr__(self, name, value):
        if self._widget is None:
            # Allows for _widget to be set
            super(ShowHideWidget, self).__setattr__(name, value)
        else:
            setattr(self._widget, name, value)

    # From widgets.Widget
    def render(self, name, value, attrs=None):
        """
        Returns self._widget's rendered HTML wrapped in HTML used to hide the
        form input by default, unless the field has a value already.
        """
        rendered_widget_html = self._widget.render(name, value, attrs=attrs)

        has_value = bool(value)
        show_text = _('Add')
        hide_text = _('Cancel')
        if has_value:
            show_text = _('Edit')
            hide_text = _('Remove')

        before_html = mark_safe(
            '<div class="show-and-hide-input">'
            '<div class="form-control-static %(add_class)s">'
            '<a href="javascript:void(0)" class="toggle-original-form-input" data-action="show">%(add_text)s <i class="icon-angle-down"></i></a>'
            '</div>'
            '<div class="original-form-widget %(input_class)s">' % {
                'add_class': 'hide' if has_value else '',
                'add_text': show_text,
                'input_class': '' if has_value else 'hide',
            }
        )
        after_html = mark_safe(
            '</div>'
            '<div class="form-control-static %(cancel_class)s">'
            '<a href="javascript:void(0)" class="toggle-original-form-input" data-action="hide">%(cancel_text)s <i class="icon-angle-up"></i></a>'
            '</div>'
            '</div>' % {
                'cancel_text': hide_text,
                'cancel_class': '' if has_value else 'hide',
            }
        )

        return format_html(u'{0}\r\n{1}\r\n{2}', before_html, rendered_widget_html, after_html)


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
        for w in self:
            buttons_html += u'''<label class="btn btn-primary %(is_active)s">%(tag)s %(label)s</label>''' % {
                'is_active': ('active' if w.is_checked() else ''),
                'tag': w.tag(),
                'label': w.choice_label,
            }

        return mark_safe(u'''<div class="btn-group" data-toggle="buttons">%s</div>''' % buttons_html)


class FormSetWidget(Widget):
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
