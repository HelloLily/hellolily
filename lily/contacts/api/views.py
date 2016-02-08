from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from lily.api.filters import ElasticSearchFilter

from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact
from lily.tenant.api.mixins import SetTenantUserMixin


class ContactViewSet(SetTenantUserMixin, viewsets.ModelViewSet):
    """
    Returns a list of all **active** contacts in the system.


    #Search#
    Searching is enabled on this API.

    Example:
    `/api/contacts/contact/?search=name:CompanyA`

    #Returns#
    * List of contacts with related fields
    """

    """
    Returns a list of all **active** contacts in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/contacts/contact/`
    - search: `/api/contacts/contact/?search=subject:Doremi`
    - order: `/api/contacts/contact/?ordering=subject,-id`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Contact.objects
    # Set the serializer class for this viewset.
    serializer_class = ContactSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter,)

    # ElasticSearchFilter: set the model type.
    model_type = 'contacts_contact'
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = (
        'id', 'first_name', 'last_name', 'full_name', 'gender', 'gender_display', 'salutation', 'salutation_display',
    )
    # OrderingFilter: set the default ordering fields.
    ordering = ('last_name', 'first_name',)

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(ContactViewSet, self).get_queryset().filter(is_deleted=False)
