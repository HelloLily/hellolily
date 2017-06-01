from rest_framework.viewsets import ModelViewSet

from .serializers import TimeLogSerializer
from ..models import TimeLog


class TimeLogViewSet(ModelViewSet):
    queryset = TimeLog.objects
    # Set the serializer class for this viewset.
    serializer_class = TimeLogSerializer

    def get_queryset(self, *args, **kwargs):
        return super(TimeLogViewSet, self).get_queryset().filter()
