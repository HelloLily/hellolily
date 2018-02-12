from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from lily.notes.api.serializers import NoteSerializer
from lily.notes.models import Note


class NoteFilter(filters.FilterSet):
    content_type = CharFilter(name='gfk_content_type__model')
    object_id = NumberFilter(name='gfk_object_id')

    class Meta:
        model = Note
        fields = ('is_pinned', )


class NoteViewSet(ModelViewSet):
    """
    This viewset contains all possible ways to manipulate a Note.
    """
    model = Note
    queryset = Note.objects  # Without .all() this filters on the tenant
    serializer_class = NoteSerializer

    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('created',)
    # DjangoFilterBackend: set the possible fields to filter on.
    filter_class = NoteFilter

    def get_queryset(self, *args, **kwargs):
        return super(NoteViewSet, self).get_queryset().filter(is_deleted=False)
