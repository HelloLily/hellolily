from django.contrib.auth import get_user_model
from django.urls import reverse

from threading import local


_thread_locals = local()


def get_current_user():
    """
    Get the current user for tenant filtering
    """
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """
    Set the current user for tenant filtering
    """
    user_cls = get_user_model()

    if isinstance(user, user_cls) or user is None:
        # User object and None are allowed
        _thread_locals.user = user


class TenantMiddleware(object):
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
