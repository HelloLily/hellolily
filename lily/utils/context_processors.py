from lily.accounts.forms import AddAccountQuickbuttonForm
from lily.cases.forms import AddCaseQuickbuttonForm
from lily.contacts.forms import AddContactQuickbuttonForm
from lily.deals.forms import AddDealQuickbuttonForm

def quickbutton_forms(request):
    return {
        'quickbutton_formsets': {
            'account': AddAccountQuickbuttonForm,
            'contact': AddContactQuickbuttonForm,
            'deal': AddDealQuickbuttonForm,
            'case': AddCaseQuickbuttonForm,
        }
    }