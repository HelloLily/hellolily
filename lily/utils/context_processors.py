from django.contrib.sites.models import Site

from lily.accounts.forms import AddAccountQuickbuttonForm
from lily.cases.forms import CreateCaseQuickbuttonForm
from lily.contacts.forms import AddContactQuickbuttonForm
from lily.deals.forms import AddDealQuickbuttonForm


def quickbutton_forms(request):
    return {
        'quickbutton_formsets': {
            'account': AddAccountQuickbuttonForm,
            'contact': AddContactQuickbuttonForm,
            'deal': AddDealQuickbuttonForm,
            'case': CreateCaseQuickbuttonForm,
        }
    }


def current_site(request):
    protocol = 'https' if request.is_secure() else 'http'
    domain = Site.objects.get_current().domain
    return {
        'SITE': '%s://%s' % (protocol, domain)
    }
