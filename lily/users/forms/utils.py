from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _


class RequiredFirstFormFormset(BaseFormSet):
    """
    This formset requires that the first form that is submitted is filled in.
    """
    def __init__(self, *args, **kwargs):
        super(RequiredFirstFormFormset, self).__init__(*args, **kwargs)

        try:
            self.forms[0].empty_permitted = False
        except IndexError:
            print "Index error in the init of required first form formset"

    def clean(self):
        if self.total_form_count() < 1:
            raise forms.ValidationError(_("We need some data before we can proceed. Fill out at least one form."))


class RequiredFormset(BaseFormSet):
    """
    This formset requires all the forms that are submitted are filled in.
    """
    # TODO: check the extra parameter to statisfy that all initial forms are filled in.
    def __init__(self, *args, **kwargs):
        super(RequiredFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
