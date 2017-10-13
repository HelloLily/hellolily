from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from rest_framework.authtoken.models import Token


class SetRemoteAddrFromForwardedFor(object):
    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # On Heroku the last in the list is guaranteed to be the real one.
            real_ip = real_ip.split(",")[-1].strip()
            request.META['REMOTE_ADDR'] = real_ip


def get_user(token):
    model = Token

    try:
        token = model.objects.select_related('user').get(key=token)
        user = token.user

        if not user.is_active:
            user = AnonymousUser()
    except model.DoesNotExist:
        user = AnonymousUser()

    return user


class TokenAuthenticationMiddleware(object):
    def process_request(self, request):
        token = request.GET.get('key', None)

        # Exclude api, because for some reason you actually can't use the token there if we already set the user here.
        if token and isinstance(request.user, AnonymousUser) and not request.path.startswith('/api/'):
            request.user = SimpleLazyObject(lambda: get_user(token))
