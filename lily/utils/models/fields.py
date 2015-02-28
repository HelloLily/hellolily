from django.db import models

from ..forms.fields import FormSetField
from ..forms.formsets import PhoneNumberFormSet, AddressFormSet, EmailAddressFormSet


class BaseFormSetField(models.ManyToManyField):
    template = None
    formset_class = None
    form_class = FormSetField

    def save_form_data(self, instance, data):
        formfield = self.formfield()
        formfield.save(instance, data, self.attname)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': self.form_class,
            'formset_class': self.formset_class,
            'template': self.template,
        }

        defaults.update(kwargs)

        return super(BaseFormSetField, self).formfield(**defaults)


class PhoneNumberFormSetField(BaseFormSetField):
    template = 'utils/formset_phone_number.html'
    formset_class = PhoneNumberFormSet


class AddressFormSetField(BaseFormSetField):
    template = 'utils/formset_address.html'
    formset_class = AddressFormSet


class EmailAddressFormSetField(BaseFormSetField):
    template = 'utils/formset_email_address.html'
    formset_class = EmailAddressFormSet
