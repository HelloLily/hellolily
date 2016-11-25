import re

from django.db.models import Manager
from django.db.models import QuerySet
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_attribute, CharField
from rest_framework.relations import ManyRelatedField, MANY_RELATION_KWARGS

from lily.utils.sanitizers import HtmlSanitizer


class RegexDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        if not data:
            raise ValidationError(_('This field is required'))

        # Regex to get the decimal value.
        regex = '([.,][0-9]{1,2}$)'
        data_split = re.split(regex, str(data))

        # Remove commas and periods.
        data = data_split[0].replace('.', '').replace(',', '')

        if len(data_split) >= 2:
            # Change comma to period for decimal separator.
            data += data_split[1].replace(',', '.')

        return data


class DynamicQuerySetManyRelatedField(ManyRelatedField):
    def __init__(self, queryset, *args, **kwargs):
        self.queryset = queryset
        super(DynamicQuerySetManyRelatedField, self).__init__(*args, **kwargs)

    def get_attribute(self, instance):
        # Can't have any relationships if not created.
        if hasattr(instance, 'pk') and instance.pk is None:
            return []

        queryset = self.queryset
        if hasattr(queryset, '__call__'):
            queryset = queryset(self.child_relation, instance)
        else:
            relationship = get_attribute(instance, self.source_attrs)
            queryset = relationship.all() if (hasattr(relationship, 'all')) else relationship
        return queryset


class DynamicQuerySetPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
        Serializer field with a special `get_queryset()` method that lets you pass
        a callable for the queryset kwarg. This enables you to limit the queryset
        based on data or context available on the serializer at runtime. This field
        also overrides the ManyRelatedField for the `many=True` kwarg so the dynamic
        queryset is actually used.
        """

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        Use DynamicQuerySetManyRelatedField so the dynamic queryset is actually
        used to filter values.
        """
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]

        list_kwargs['queryset'] = kwargs.get('queryset')

        return DynamicQuerySetManyRelatedField(**list_kwargs)

    def get_queryset(self):
        """
        Return the queryset for a related field. If the queryset is a callable,
        it will be called with one argument which is the field instance, and
        should return a queryset or model manager.
        """
        queryset = self.queryset
        if hasattr(queryset, '__call__'):
            queryset = queryset(self)
        elif isinstance(queryset, (QuerySet, Manager)):
            # Ensure queryset is re-evaluated whenever used.
            # Note that actually a `Manager` class may also be used as the
            # queryset argument. This occurs on ModelSerializer fields,
            # as it allows us to generate a more expressive 'repr' output
            # for the field.
            # Eg: 'MyRelationship(queryset=ExampleModel.objects.all())'
            queryset = queryset.all()
        return queryset


class SanitizedHtmlCharField(CharField):
    """
    A field that sanitizes the incoming html.
    """

    def __init__(self, **kwargs):
        # Override the defaults of these kwargs.
        kwargs['allow_blank'] = kwargs.get('allow_blank', True)
        kwargs['required'] = kwargs.get('required', False)

        super(SanitizedHtmlCharField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        value = super(SanitizedHtmlCharField, self).to_internal_value(data)
        return HtmlSanitizer(value).clean().render()
