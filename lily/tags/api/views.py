from lily.utils.api.views import RelatedModelViewSet
from ..models import Tag
from .serializers import TagSerializer


class TagViewSet(RelatedModelViewSet):

    queryset = Tag.objects
    serializer_class = TagSerializer
    related_model = None

    def _get_related_queryset(self, object_pk):
        return self._get_related_object(object_pk).tags
