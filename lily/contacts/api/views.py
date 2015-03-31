from rest_framework import viewsets

from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact


class ContactViewSet(viewsets.ModelViewSet):
    """
    This viewset contains all possible ways to manipulate a Contact.
    """
    queryset = Contact.objects  # Without .all() this filters on the tenant
    serializer_class = ContactSerializer

    def get_queryset(self):
        return super(ContactViewSet, self).get_queryset().filter(is_deleted=False)

    # def retrieve(self, request, pk=None):
    #     # Haal een object op uit ES
    #     pass
    #
    # def list(self, request):
    #     # Haal een lijst op uit ES
    #     pass
    #
    # def create(self, request):
    #     # Schrijf een contact naar de DB
    #     pass
    #
    # def update(self, request, pk=None):
    #     # Scrhijf een bestaand contact naar de DB
    #     pass
    #
    # def partial_update(self, request, pk=None):
    #     # Schrijf een bestaand contact naar de DB
    #     pass
    #
    # def destroy(self, request, pk=None):
    #     # Verwijder een contact uit de db
    #     pass
