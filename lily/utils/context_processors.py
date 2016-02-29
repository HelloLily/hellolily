from django.contrib.sites.models import Site

from .functions import is_ajax


def current_site(request):
    if is_ajax(request):
        return {}

    protocol = 'https' if request.is_secure() else 'http'
    domain = Site.objects.get_current().domain
    return {
        'SITE': '%s://%s' % (protocol, domain)
    }
