from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from lily.notes.api.serializers import NoteSerializer
from lily.notes.models import Note


class NoteViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
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

    def get_queryset(self, *args, **kwargs):
        return super(NoteViewSet, self).get_queryset().filter(is_deleted=False)
