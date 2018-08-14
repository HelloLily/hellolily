import logging

from django.forms import Field, CharField, ValidationError
from django.utils.translation import ugettext_lazy as _

from .widgets import TagInput, FormSetWidget

logger = logging.getLogger(__name__)


class TagsField(CharField):
    """
    The field used for selecting tags
    """
    widget = TagInput

    def __init__(self, choices=(), *args, **kwargs):
        super(TagsField, self).__init__(*args, **kwargs)
        self.choices = choices

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

    def to_python(self, value):
        value = super(TagsField, self).to_python(value)
        return value.split(',')


class FormSetField(Field):
    widget = FormSetWidget
    is_formset = True

    def __init__(
        self,
        queryset=None,
        formset_class=None,
        template=None,
        form_attrs=None,
        related_name=None,
        limit_choices_to=None,
        *args,
        **kwargs
    ):
        self.queryset = queryset
        self.formset_class = formset_class
        self.template = template
        self.form_attrs = form_attrs
        self.related_name = related_name
        self.limit_choices_to = limit_choices_to

        widget = self.widget(self.queryset)

        super(FormSetField, self).__init__(widget=widget, *args, **kwargs)

    def validate(self, value):
        if not value.is_valid():
            if self.error_messages and 'invalid' in self.error_messages:
                raise ValidationError(self.error_messages['invalid'])
            else:
                raise ValidationError(code='invalid', message=_('Invalid input'))

    def clean(self, value):
        return super(FormSetField, self).clean(value)

    def widget_attrs(self, widget):
        attrs = super(FormSetField, self).widget_attrs(widget)

        attrs.update({
            'formset_class': self.formset_class,
            'queryset': self.queryset,
            'template': self.template,
        })

        return attrs

    def _get_form_attrs(self):
        return self._form_attrs

    def _set_form_attrs(self, value):
        self._form_attrs = self.widget.form_attrs = value

    form_attrs = property(_get_form_attrs, _set_form_attrs)

    def save(self, instance, formset, attname):
        formset.related_name = self.related_name or attname
        formset.related_instance = instance
        formset.save()
