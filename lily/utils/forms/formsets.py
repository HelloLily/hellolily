from django.forms.models import BaseModelFormSet, modelformset_factory

from ..models.models import PhoneNumber, Address, EmailAddress
from .forms import PhoneNumberBaseForm, AddressBaseForm, EmailAddressBaseForm


class BaseM2MFormSet(BaseModelFormSet):
    """
    The formset used for custom saving of a formset for a many to many relation
    """
    def save(self, commit=True):
        """
        With many to many fields you want to add the relation after saving the objects.

        Args:
            commit (boolean, optional): Specify whether to actually save or just return the list of instances.
        """
        instance_list = super(BaseM2MFormSet, self).save(commit=commit)

        if commit and hasattr(self, 'related_instance') and hasattr(self, 'related_name'):
            for form in self.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    getattr(self.related_instance, self.related_name).add(form.instance)

        return instance_list


class BaseFKFormSet(BaseModelFormSet):
    """
    The formset used for custom saving of a formset for a foreign key relation
    """
    def save(self, commit=True):
        """
        With foreign keys you want to the relation of new objects prior to saving the objects

        Args:
            commit (boolean, optional): Specify whether to actually save or just return the list of instances.
        """
        if commit and hasattr(self, 'related_instance') and hasattr(self, 'related_name'):
            for form in self.forms:
                if self.related_name in [f.name for f in form.instance._meta.get_fields()]:
                    setattr(form.instance, self.related_name, self.related_instance)

        return super(BaseFKFormSet, self).save(commit)


PhoneNumberFormSet = modelformset_factory(PhoneNumber,
                                          form=PhoneNumberBaseForm,
                                          formset=BaseM2MFormSet,
                                          can_delete=True,
                                          extra=0)
AddressFormSet = modelformset_factory(Address, form=AddressBaseForm, formset=BaseM2MFormSet, can_delete=True, extra=0)
EmailAddressFormSet = modelformset_factory(EmailAddress,
                                           form=EmailAddressBaseForm,
                                           formset=BaseM2MFormSet,
                                           can_delete=True,
                                           extra=0)
