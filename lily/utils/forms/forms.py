from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class SugarCsvImportForm(Form):
    """
    Form in which a csv file can be uploaded from which
    accounts or contacts can be imported for the logged in tenant.
    """
    csvfile = forms.FileField(label=_('CSV'))
    model = forms.ChoiceField(label=_('Import rows as'), choices=(('contact', _('Contacts')),
                                                                  ('account', _('Accounts')),
                                                                  ('function', _('Functions'))))
    sugar_import = forms.ChoiceField(label=_('From source:'), choices=((1, _('Sugar')), (0, _('Other'))))
