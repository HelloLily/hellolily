from django_filters import CharFilter, NumberFilter
from rest_framework.filters import DjangoFilterBackend, FilterSet, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from lily.notes.api.serializers import NoteSerializer
from lily.notes.models import Note


class NoteFilter(FilterSet):
    content_type = CharFilter(name='gfk_content_type__model')
    object_id = NumberFilter(name='gfk_object_id')

    class Meta:
        model = Note
        fields = ('is_pinned', )


class NoteViewSet(ModelViewSet):
    """
    Notes can be used to store information in the activity stream of an object.

    retrieve:
    Returns the given note.

    list:
    Returns a list of all the notes.

    create:
    Creates a new note.

    update:
    Overwrites the whole note with the given data.

    partial_update:
    Updates just the fields in the request data of the given note.

    delete:
    Deletes the given note.
    """
    model = Note
    queryset = Note.objects  # Without .all() this filters on the tenant
    serializer_class = NoteSerializer

    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('created',)
    # DjangoFilterBackend: set the possible fields to filter on.
    filter_class = NoteFilter

    def get_queryset(self, *args, **kwargs):
        return super(NoteViewSet, self).get_queryset().filter(is_deleted=False)
