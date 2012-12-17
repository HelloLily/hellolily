try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
from django.core.urlresolvers import reverse


_thread_locals = local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


class TenantMiddleWare(object):
    """
    Make the user that makes the request retrievable from anywhere.
    """
    def process_request(self, request):
        """
        Save a reference to the user in local threading. When in Django admin,
        make sure to it to prevent the Middleware from filtering the QuerySets
        to the user's tenant.
        """
        if request.path.startswith(reverse('admin:index')):
            _thread_locals.user = None
        else:
            _thread_locals.user = getattr(request, 'user', None)
