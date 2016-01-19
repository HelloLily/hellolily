from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet


from .serializers import DealSerializer, DealNextStepSerializer
from ..models import Deal, DealNextStep


class DealStagesList(APIView):
    def get(self, request, format=None):
        return Response(Deal.STAGE_CHOICES)


class DealViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    """
    List all deals for a tenant.
    """
    model = Deal
    serializer_class = DealSerializer
    queryset = Deal.objects

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        return queryset

    def partial_update(self, request, *args, **kwargs):
        deal = Deal.objects.get(pk=kwargs.get('pk'))
        serializer = DealSerializer(deal, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class DealNextStepList(APIView):
    model = DealNextStep
    serializer_class = DealNextStepSerializer

    def get(self, request, format=None):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        serializer = DealNextStepSerializer(queryset, many=True)
        return Response(serializer.data)
