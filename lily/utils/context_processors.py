from lily.accounts.forms import AddAccountMinimalForm
from lily.contacts.forms import AddContactMinimalForm
from lily.deals.forms import AddDealForm

def quickbutton_forms(request):
    return {
        'quickbutton_formsets': {
            'account': AddAccountMinimalForm,
            'contact': AddContactMinimalForm,
            'deal': AddDealForm,
        }
    }