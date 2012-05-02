from lily.accounts.forms import AddAccountMinimalForm
from lily.contacts.forms import AddContactMinimalForm

def quickbutton_forms(request):
    return {
        'quickbutton_form_account': AddAccountMinimalForm,
        'quickbutton_form_contact': AddContactMinimalForm
    }