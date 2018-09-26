from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lily.utils.api.permissions import IsFeatureAvailable

from .serializers import ObjectFileSerializer
from ..models import ObjectFile


class ObjectFileViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsFeatureAvailable, )
    queryset = ObjectFile.objects
    serializer_class = ObjectFileSerializer
    required_tier = 1
    swagger_schema = None

    def get_queryset(self, *args, **kwargs):
        return super(ObjectFileViewSet, self).get_queryset().filter()
