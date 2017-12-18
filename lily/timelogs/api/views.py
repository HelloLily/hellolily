from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lily.utils.api.permissions import IsFeatureAvailable

from .serializers import TimeLogSerializer
from ..models import TimeLog


class TimeLogViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsFeatureAvailable, )
    queryset = TimeLog.objects
    # Set the serializer class for this viewset.
    serializer_class = TimeLogSerializer
    required_tier = 1

    def get_queryset(self, *args, **kwargs):
        return super(TimeLogViewSet, self).get_queryset().filter()
