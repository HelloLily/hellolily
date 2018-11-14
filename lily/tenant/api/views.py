from django.conf import settings
from rest_framework import mixins
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.messaging.email.models.models import EmailAccount
from lily.tenant.api.serializers import TenantSerializer
from lily.tenant.models import Tenant
from lily.users.api.serializers import LilyUserSerializer
from lily.utils.functions import has_required_tier


class TenantViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Tenant.objects
    # Set the serializer class for this viewset.
    serializer_class = TenantSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = ()
    # Disable pagination for this api.
    pagination_class = None
    swagger_schema = None

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant.
        """
        return super(TenantViewSet, self).get_queryset().filter(pk=self.request.user.tenant_id)

    @list_route(methods=['GET'])
    def admin(self, request):
        account_admin = request.user.tenant.admin

        context = self.get_serializer_context()
        serializer = LilyUserSerializer(instance=account_admin, context=context)

        return Response({'admin': serializer.data})

    @list_route(methods=['GET'])
    def info(self, request):
        object_counts = {
            'cases': Case.objects.count(),
            'deals': Deal.objects.count()
        }

        trial_remaining = request.user.tenant.billing.trial_remaining

        if not has_required_tier(1):
            account_count = Account.objects.filter(is_deleted=False).count()
            contact_count = Contact.objects.filter(is_deleted=False).count()
            email_account_count = EmailAccount.objects.filter(is_deleted=False).count()

            limit_reached = {
                'accounts': account_count >= settings.FREE_PLAN_ACCOUNT_CONTACT_LIMIT,
                'contacts': contact_count >= settings.FREE_PLAN_ACCOUNT_CONTACT_LIMIT,
                'email_accounts': email_account_count >= settings.FREE_PLAN_EMAIL_ACCOUNT_LIMIT,
            }
        else:
            limit_reached = None

        return Response({
            'results': {
                'object_counts': object_counts,
                'limit_reached': limit_reached,
                'trial_remaining': trial_remaining,
            }
        })
