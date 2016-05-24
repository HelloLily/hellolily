from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from lily.notes.api.serializers import NoteSerializer
from lily.notes.models import Note
from lily.tenant.api.mixins import SetTenantUserMixin


class NoteViewSet(SetTenantUserMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  # mixins.ListModelMixin,  # No list because that will be in the historylist
                  GenericViewSet):
    """
    This viewset contains all possible ways to manipulate a Note.
    """
    model = Note
    queryset = Note.objects  # Without .all() this filters on the tenant
    serializer_class = NoteSerializer

    def get_queryset(self, *args, **kwargs):
        return super(NoteViewSet, self).get_queryset().filter(is_deleted=False)
