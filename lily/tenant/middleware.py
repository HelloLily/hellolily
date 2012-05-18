try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)


class TenantMiddleWare(object):
    """
    Make the user that makes the request retrievable from anywhere.
    """
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)