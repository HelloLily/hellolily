from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin

from lily.calls.api.serializers import CallSerializer
from lily.calls.models import Call
from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact, Function
from lily.users.models import LilyUser


class ContactViewSet(ModelChangesMixin, viewsets.ModelViewSet):
    """
    Returns a list of all **active** contacts in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/contacts/`
    - search: `/api/contacts/?search=subject:Doremi`
    - order: `/api/contacts/?ordering=subject,-id`

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
        if 'filter_deleted' in self.request.GET:
            if self.request.GET.get('filter_deleted') == 'False':
                return super(ContactViewSet, self).get_queryset()

        return super(ContactViewSet, self).get_queryset().filter(is_deleted=False)

    @list_route(methods=['patch', ])
    def toggle_activation(self, request):
        """
        Toggle if the contact is active at account.
        """
        contact_id = request.data.get('contact')
        account_id = request.data.get('account')
        is_active = request.data.get('is_active')

        try:
            func = Function.objects.get(contact=contact_id, account=account_id)
        except Function.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            func.is_active = is_active
            func.save()

            return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['GET'])
    def calls(self, request, pk=None):
        """
        Gets the calls for the given contact.
        """
        phone_numbers = []
        contact = self.get_object()

        for number in contact.phone_numbers.all():
            phone_numbers.append(number.number)

        calls = []

        call_objects = Call.objects.filter(
            status=Call.ANSWERED,
            type=Call.INBOUND,
            caller_number__in=phone_numbers,
            created__isnull=False,
        )

        if call_objects:
            calls = CallSerializer(call_objects, many=True).data

            for call in calls:
                call['contact'] = contact.full_name

                user = LilyUser.objects.filter(internal_number=call.get('internal_number')).first()

                if user:
                    call['user'] = user.full_name

        return Response({'objects': calls})
