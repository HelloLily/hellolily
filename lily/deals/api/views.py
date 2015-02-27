from datetime import date, timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from lily.users.models import LilyUser

from .serializers import DealSerializer
from ..models import Deal


class DealList(APIView):
    serializer_class = DealSerializer

    def get(self, request, format=None):
        queryset = Deal.objects.filter(tenant_id=self.request.user.tenant_id)

        # TODO: LILY-630: Expand this API. Can be used as a general API where the user has to manually set url params
        # stage = self.request.QUERY_PARAMS.get('stage', None)
        # if stage is not None:
        #     queryset = queryset.filter(stage=stage)

        serializer = DealSerializer(queryset, many=True)

        return Response(serializer.data)


class DealCommunicationList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        users = LilyUser.objects.filter(tenant_id=self.request.user.tenant_id, is_active=True)

        statistics = []

        for user in users:
            deals = Deal.objects.filter(assigned_to=user)

            # Count the deals where:
            # - Deal is assigned to user
            # - Deal was made for a new business
            # - Deal stage is proposal sent
            # - Between 7 and 30 days old
            follow_up = deals.filter(
                assigned_to=user,
                new_business=True,
                stage=Deal.PENDING_STAGE,
                created__range=(
                    date.today() - timedelta(days=30),
                    date.today() - timedelta(days=7)
                )
            ).count()

            # Count the deals where:
            # - Deal is assigned to user
            # - Deal was made for a new business
            # - Deal stage is won
            # - Feedback form was not sent
            # - Between 30 and 120 days old
            feedback = deals.filter(
                assigned_to=user,
                new_business=True,
                stage=Deal.WON_STAGE,
                feedback_form_sent=False,
                created__range=(
                    date.today() - timedelta(days=120),
                    date.today() - timedelta(days=30)
                )
            ).count()

            statistics.append({
                'user': user.full_name,
                'follow_up': follow_up,
                'feedback': feedback
            })

        return Response(statistics)


class DealWonWrittenList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        users = LilyUser.objects.filter(tenant_id=self.request.user.tenant_id, is_active=True)

        statistics = []

        for user in users:
            # Get deal that are assigned to user and were created 75 days or less ago
            deals = Deal.objects.filter(
                assigned_to=user,
                created__range=(date.today() - timedelta(days=75), date.today())
            )

            # Count the amount of deals won
            deals_won = deals.filter(stage=Deal.WON_STAGE).count()
            # Count the amount of deals that have been sent
            deals_sent = deals.filter(stage=Deal.PENDING_STAGE).count()

            amount_once = 0
            amount_recurring = 0

            # Count the actual money made
            for deal in deals:
                amount_once += deal.amount_once
                amount_recurring += deal.amount_recurring

            statistics.append({
                'user': user.full_name,
                'deals_won': deals_won,
                'deals_sent': deals_sent,
                'amount_once': amount_once,
                'amount_recurring': amount_recurring,
                'total_amount': amount_once + amount_recurring
            })

        return Response(statistics)
