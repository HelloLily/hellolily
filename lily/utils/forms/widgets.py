import json

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.forms.formsets import BaseFormSet
from django.forms.widgets import TextInput, Widget, RadioSelect, Textarea
from django.forms.utils import flatatt
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
        attrs = dict(attrs)
        attrs.update(name=name)
        attrs.update(value=value)
        final_attrs = self.build_attrs(self.attrs, attrs)

        return super(TagInput, self).render(name, value, final_attrs)

    def build_attrs(self, attrs=None, extra_attrs=None, **kwargs):
        attrs = dict(attrs, **kwargs)
        extra_attrs = extra_attrs or {}
        extra_attrs.update({
            'data-choices': ','.join(self.choices),
        })

        if 'class' not in kwargs:
            extra_attrs.update({'class': 'tags'})
        attrs.update(extra_attrs)

        return super(TagInput, self).build_attrs(self.attrs, attrs=attrs)


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
            button_attrs.update({'class': 'hl-primary-btn'})
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
        attrs = dict(attrs)
        attrs.update(name=name)
        attrs.update(value=value)
        attrs.update(type=self.input_type)

        input_attrs = self.build_attrs(self.attrs, attrs)

        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self._format_value(value))
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])

        div_attrs = dict([(key, conditional_escape(val)) for key, val in self.div_attrs.items()])
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        button_attrs = dict([(key, conditional_escape(val)) for key, val in self.button_attrs.items()])

        html = self.html_template % dict(
            div_attrs=flatatt(div_attrs),
            input_attrs=flatatt(input_attrs),
            button_attrs=flatatt(button_attrs),
            icon_attrs=flatatt(icon_attrs)
        )

        return mark_safe(force_text(html))


class HorizontalRadioSelect(RadioSelect):
    template_name = 'email/horizontal_select.html'


class FormSetWidget(Widget):
    choices = None

    def __init__(self, queryset=None, form_attrs=None, attrs=None):
        super(FormSetWidget, self).__init__(attrs)

        self.queryset = queryset
        self.form_attrs = form_attrs

    def render(self, name, value, attrs=None):
        attrs = dict(attrs)
        attrs.update(name=name)
        attrs.update(value=value)
        final_attrs = self.build_attrs(self.attrs, attrs)

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
        attrs = dict(attrs, *args)
        attrs.update(name=name)
        attrs.update(value=value)
        final_attrs = self.build_attrs(self.attrs, attrs)

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
        default_attrs = {'class': 'inbox-editor inbox-wysihtml5 form-control'}
        if attrs:
            default_attrs.update(attrs)
        super(Wysihtml5Input, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        attrs = dict(attrs)
        attrs.update(name=name)
        attrs.update(value=value)
        final_attrs = self.build_attrs(self.attrs, attrs)
        return render_to_string('utils/wysihtml5.html', {
            'name': name,
            'value': value,
            'attrs': final_attrs,
        })
