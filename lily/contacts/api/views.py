from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin, DataExistsMixin, ElasticModelMixin, NoteMixin
from lily.calls.api.serializers import CallRecordSerializer
from lily.calls.models import CallRecord
from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact


class ContactViewSet(ElasticModelMixin, ModelChangesMixin, DataExistsMixin, NoteMixin, viewsets.ModelViewSet):
    """
    Contacts are people you want to store the information of.

    retrieve:
    Returns the given contact.

    list:
    Returns a list of all the existing active contacts.

    create:
    Creates a new contact.

    update:
    Overwrites the whole contact with the given data.

    > Note: If Moneybird integration is setup each update will also send the contact's data to Moneybird.

    partial_update:
    Updates just the fields in the request data of the given contact.

    > Note: If Moneybird integration is setup each update will also send the contact's data to Moneybird.

    delete:
    Deletes the given contact.

    changes:
    Returns all the changes performed on the given contact.
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Contact.elastic_objects
    # Set the serializer class for this viewset.
    serializer_class = ContactSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, filters.DjangoFilterBackend, )

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('first_name', 'last_name', 'created', 'modified', 'accounts__name', 'status', )
    # OrderingFilter: set the default ordering fields.
    ordering = ('last_name', 'first_name', )
    # SearchFilter: set the fields that can be searched on.
    search_fields = ('accounts__name', 'accounts__phone_numbers', 'description', 'email_addresses',
                     'full_name', 'phone_numbers', 'tags', )
    filter_fields = ('accounts', )

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        if 'filter_deleted' in self.request.GET:
            if self.request.GET.get('filter_deleted') in ['False', 'false']:
                return super(ContactViewSet, self).get_queryset()

        return super(ContactViewSet, self).get_queryset().filter(is_deleted=False)

    @swagger_auto_schema(auto_schema=None)
    @detail_route(methods=['GET', ])
    def calls(self, request, pk=None):
        contact = self.get_object()

        phone_numbers = contact.phone_numbers.all().values_list('number', flat=True)

        calls = CallRecord.objects.filter(
            Q(caller__number__in=phone_numbers) | Q(destination__number__in=phone_numbers)
        ).order_by(
            '-start'
        )[:100]

        serializer = CallRecordSerializer(calls, many=True, context={'request': request})

        return Response({'results': serializer.data})
