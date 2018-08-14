from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lily.utils.api.permissions import IsFeatureAvailable

from .serializers import TimeLogSerializer
from ..models import TimeLog


class TimeLogViewSet(ModelViewSet):
    """
    retrieve:
    Returns the given time log.

    list:
    Returns a list of all the time logs.

    create:
    Creates a new time log.

    update:
    Overwrites the whole time log with the given data.

    partial_update:
    Updates just the fields in the request data of the given time log.

    delete:
    Deletes the given time log.
    """
    permission_classes = (
        IsAuthenticated,
        IsFeatureAvailable,
    )
    queryset = TimeLog.objects
    # Set the serializer class for this viewset.
    serializer_class = TimeLogSerializer
    required_tier = 1

    def get_queryset(self, *args, **kwargs):
        return super(TimeLogViewSet, self).get_queryset().filter()
