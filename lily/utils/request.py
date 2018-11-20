from django.conf import settings


def is_external_referer(request):
    """ Returns true or false depending on if the referer in the request is external to the Lily domain."""
    return 'HTTP_REFERER' in request.META and not any(
        allowed_host in request.META['HTTP_REFERER'] for allowed_host in settings.ALLOWED_HOSTS
    )
