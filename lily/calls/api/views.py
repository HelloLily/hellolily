import json

from channels import Group
from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework import viewsets, mixins
from rest_framework.decorators import list_route
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from lily.users.models import LilyUser
from lily.search.functions import search_number
from lily.utils.functions import parse_phone_number

from .serializers import CallSerializer, CallRecordSerializer
from ..models import Call, CallRecord


class CallViewSet(viewsets.ModelViewSet):
    """
    Returns a list of all calls in the system.
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Call.objects
    # Set the serializer class for this viewset.
    serializer_class = CallSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter,)
    # OrderingFilter: set the default ordering fields.
    ordering = ('id',)

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(CallViewSet, self).get_queryset().filter()

    def create(self, request, *args, **kwargs):
        """
        Sends a websocket message to the user with the corresponding internal number
        """
        response = super(CallViewSet, self).create(request, *args, **kwargs)
        called_user = LilyUser.objects.filter(
            internal_number=request.data['internal_number'],
            tenant_id=request.user.tenant_id
        ).first()

        if not called_user:
            return response

        caller_number = parse_phone_number(request.data['caller_number'])
        result = search_number(called_user.tenant_id, caller_number)
        search_data = result.get('data', {})
        accounts = search_data['accounts']
        contacts = search_data['contacts']

        # If a single accounts with this number has been found, show information about and link to this account.
        if accounts and len(accounts) == 1:
            data = {
                'destination': 'account',
                'icon': static('app/images/notification_icons/account.png'),
                'params': {
                    'name': accounts[0].name,
                    'number': caller_number,
                    'id': accounts[0].id,
                },
            }

            # If there are also contacts, change the title. If there's only one contact, we prepend this contacts
            # name, else we append "Somebody from"
            if contacts:
                if len(contacts) > 1:
                    data['params']['name'] = 'Somebody from %s' % data['params']['name']
                else:
                    data['params']['name'] = '%s from %s' % (contacts[0].full_name, data['params']['name'])

        # If there are contacts but no accounts, show information about and link to the first contact.
        elif contacts:
            data = {
                'destination': 'contact',
                'icon': static('app/images/notification_icons/contact.png'),
                'params': {
                    'name': contacts[0].full_name,
                    'number': caller_number,
                    'id': contacts[0].id,
                },
            }

        # If no account or contact has been found, use the name provided by VoIPGRID.
        else:
            data = {
                'destination': 'create',
                'icon': static('app/images/notification_icons/add-account.png'),
                'params': {
                    'name': request.data.get('caller_name'),
                    'number': caller_number,
                },
            }

        # Sends the data as a notification event to the user who picked up the phone.
        Group('user-%s' % called_user.id).send({
            'text': json.dumps({
                'event': 'notification',
                'data': data,
            }),
        })

        return response

    @list_route(methods=['GET'])
    def latest(self, request):
        """
        Gets the latest call of the current user based on internal number.
        """
        user = self.request.user
        internal_number = user.internal_number
        call = Call.objects.filter(internal_number=internal_number, status=Call.ANSWERED).last()

        if call:
            call = self.get_serializer(call).data

        return Response({'call': call})


class CallRecordViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = CallRecord.objects
    # Set the serializer class for this viewset.
    serializer_class = CallRecordSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter,)
    # OrderingFilter: set the default ordering fields.
    ordering = ('start', )

    @list_route(methods=['GET'])
    def latest(self, request):
        """
        Gets the latest call of the current user based on internal number.
        """
        user = self.request.user
        internal_number = user.internal_number

        call = CallRecord.objects.filter(destination__internal_number=internal_number).order_by('start', 'end').last()

        if call:
            call = self.get_serializer(call).data

        return Response({'call': call})
