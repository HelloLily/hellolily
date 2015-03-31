from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from lily.notes.api.serializers import NoteSerializer
from lily.notes.models import Note


class NoteViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  # mixins.ListModelMixin,  # No list because that will be in the historylist
                  GenericViewSet):
    """
    This viewset contains all possible ways to manipulate a Note.
    """
    queryset = Note.objects  # Without .all() this filters on the tenant
    serializer_class = NoteSerializer

    def get_queryset(self, *args, **kwargs):
        return super(NoteViewSet, self).get_queryset().filter(is_deleted=False)

        # def retrieve(self, request, pk=None):
        #     # Haal een object op uit ES
        #     pass
        #
        # def list(self, request):
        #     # Haal een lijst op uit ES
        #     pass
        #
        # def create(self, request):
        #     # Schrijf een note naar de DB
        #     pass
        #
        # def update(self, request, pk=None):
        #     # Scrhijf een bestaand note naar de DB
        #     pass
        #
        # def partial_update(self, request, pk=None):
        #     # Schrijf een bestaand note naar de DB
        #     pass
        #
        # def destroy(self, request, pk=None):
        #     # Verwijder een note uit de db
        #     pass
