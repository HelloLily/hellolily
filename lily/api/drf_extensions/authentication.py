import hashlib
import hmac

from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import BaseAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import PermissionDenied

from lily.deals.models import Deal
from lily.integrations.credentials import get_credentials
from lily.users.models import LilyUser
from lily.tenant.middleware import set_current_user
from lily.utils.functions import has_required_tier


class TokenGETAuthentication(TokenAuthentication):
    """
    Allows for token authentication based on the GET parameter.
    """

    def authenticate(self, request):
        token = request.GET.get('key', None)
        if not token:
            return None

        return self.authenticate_credentials(token)


class LilyApiAuthentication(BaseAuthentication):
    authenticators = (SessionAuthentication, TokenAuthentication, TokenGETAuthentication)

    def authenticate(self, request):
        for authenticator_cls in self.authenticators:
            authenticator = authenticator_cls()

            auth_tuple = authenticator.authenticate(request)
            if auth_tuple:
                if isinstance(authenticator, TokenAuthentication) or isinstance(authenticator, TokenGETAuthentication):
                    if not has_required_tier(2, tenant=auth_tuple[0].tenant):
                        # Tenant is on free plan, so no external API access.
                        raise PermissionDenied({
                            'detail': (
                                'API access has been disabled because you are on the free plan.'
                                'Please upgrade to continue using the API'
                            )
                        })
                break
        else:
            # All authentication failed.
            return None

        # Set the current user for the tenant filters.
        set_current_user(auth_tuple[0])

        return auth_tuple


class PandaDocSignatureAuthentication(BaseAuthentication):
    def authenticate(self, request):
        data = request.data[0].get('data')
        metadata = data.get('metadata')
        deal = metadata.get('deal')

        if not deal:
            # No shared key set by the user so we have no way to verify the request.
            raise PermissionDenied({'detail': _('No deal found.')})

        # Use the deal to retrieve the tenant.
        deal = Deal.objects.get(pk=metadata.get('deal'))

        # Get the shared key which has been provided by PandaDoc.
        credentials = get_credentials('pandadoc', deal.tenant)

        shared_key = credentials.integration_context.get('shared_key')

        if not shared_key:
            # No shared key set by the user so we have no way to verify the request.
            raise PermissionDenied({
                'detail': _('No shared key found. Please go to your PandaDoc webhook settings and provide the key.')
            })

        # A shared key has been stored. So create HMAC based on given values and check if it's valid.
        signature = hmac.new(str(shared_key), str(request.body), digestmod=hashlib.sha256).hexdigest()

        if signature != request.GET.get('signature'):
            raise PermissionDenied({
                'detail': _('Invalid request. Either the provided shared key or signature is incorrect')
            })

        user = metadata.get('user')

        if user:
            user = LilyUser.objects.get(pk=user)
        else:
            user = deal.assigned_to

        set_current_user(user)

        return (user, None)
