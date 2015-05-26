from rest_framework import viewsets
from lily.api.filters import ElasticSearchFilter

from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact


class ContactViewSet(viewsets.ModelViewSet):
    """
    Returns a list of all **active** contacts in the system.


    #Search#
    Searching is enabled on this API.

    Example:
    `/api/contacts/contact/?search=name:CompanyA`

    #Returns#
    * List of contacts with related fields
    """
    queryset = Contact.objects  # Without .all() this filters on the tenant
    serializer_class = ContactSerializer
    filter_backends = (ElasticSearchFilter,)
    model_type = 'contacts_contact'

    def get_queryset(self):
        return super(ContactViewSet, self).get_queryset().filter(is_deleted=False)
