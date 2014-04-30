from django.contrib.sites.models import Site

from lily.accounts.forms import AddAccountQuickbuttonForm
from lily.cases.forms import CreateCaseQuickbuttonForm
from lily.contacts.forms import AddContactQuickbuttonForm
from lily.deals.forms import CreateDealQuickbuttonForm
from lily.utils.functions import is_ajax


def quickbutton_forms(request):
    return {
        'quickbutton_formsets': {
            'account': AddAccountQuickbuttonForm,
            'contact': AddContactQuickbuttonForm,
            'deal': CreateDealQuickbuttonForm,
            'case': CreateCaseQuickbuttonForm,
        }
    }


def current_site(request):
    if is_ajax(request):
        return {}

    protocol = 'https' if request.is_secure() else 'http'
    domain = Site.objects.get_current().domain
    return {
        'SITE': '%s://%s' % (protocol, domain)
    }
